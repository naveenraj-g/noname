import { BetterAuthPlugin } from "better-auth";
import { createAuthEndpoint, APIError } from "better-auth/api";
import {
  TAuthClientToken,
  TAuthTokenResponse,
  TUserInfo,
} from "./models/keycloak/keycloak";
import axios from "axios";
import { createAndSyncSession, parseKeycloakError } from "./utils";
import { deleteSessionCookie } from "better-auth/cookies";
import nodemailer from "nodemailer";
import { jwtVerify, SignJWT } from "jose";
import { JWTExpired, JWTInvalid } from "jose/errors";
import { getKeycloakAdminClientToken } from "./utils/getKeycloakToken";
import * as z from "zod";

export const keycloakProvider = ({
  appUrl,
  baseUrl,
  clientId,
  clientSecret,
  realm,
  emailUser,
  emailPass,
  autoSignIn = true,
  providerId = "keycloak",
}: {
  appUrl: string;
  baseUrl: string;
  realm: string;
  clientId: string;
  clientSecret: string;
  autoSignIn?: boolean;
  providerId?: string;
  emailUser: string;
  emailPass: string;
}): BetterAuthPlugin => {
  const issuerUrl = `${baseUrl}/realms/${realm}`;
  const adminIssuerUrl = `${baseUrl}/admin/realms/${realm}`;

  const keyclockEndpoints = {
    issuer: issuerUrl,
    authorization_endpoint: `${issuerUrl}/protocol/openid-connect/auth`,
    token_endpoint: `${issuerUrl}/protocol/openid-connect/token`,
    introspection_endpoint: `${issuerUrl}/protocol/openid-connect/token/introspect`,
    userinfo_endpoint: `${issuerUrl}/protocol/openid-connect/userinfo`,
    end_session_endpoint: `${issuerUrl}/protocol/openid-connect/logout`,
    admin_user: `${adminIssuerUrl}/users`,
  };

  return {
    id: "keycloakProvider",
    schema: {
      user: {
        fields: {
          keycloakUserid: {
            type: "string",
            required: false,
            unique: true,
          },
        },
      },
      // keycloak_user: {
      //   modelName: "keycloakUser",
      //   fields: {
      //     keycloakUserId: {
      //       type: "string",
      //       required: true,
      //     },
      //     userId: {
      //       type: "string",
      //       required: true,
      //       references: {
      //         model: "user",
      //         field: "id",
      //         onDelete: "cascade",
      //       },
      //     },
      //   },
      // },
    },

    init() {
      if (!baseUrl || !realm || !clientId || !clientSecret || !appUrl) {
        throw new APIError("BAD_REQUEST", {
          message: "Missing Keycloak configuration.",
        });
      }

      if (process.env.NODE_ENV !== "production") {
        console.log("[Keycloak Plugin] initialized for realm:", realm);
      }
    },

    endpoints: {
      // 🔐 Sign-in
      signinKeycloak: createAuthEndpoint(
        "/keycloakProvider/signin",
        {
          method: "POST",
          body: z.object({
            usernameorEmail: z
              .string()
              .describe("Email or Username of the user"),
            password: z.string().describe("The password of the user"),
            rememberMe: z
              .boolean()
              .describe("Remember the user session")
              .optional(),
            callbackURL: z
              .string()
              .describe("The URL to redirect to after email verification")
              .optional(),
          }),
        },
        async (ctx) => {
          const { usernameorEmail, password, rememberMe, callbackURL } =
            await ctx.body;

          if (!usernameorEmail || !password) {
            return ctx.error("BAD_REQUEST", { message: "Missing credentials" });
          }

          try {
            // Exchange credentials for token
            const tokenRes = await axios.post<TAuthTokenResponse>(
              keyclockEndpoints.token_endpoint,
              new URLSearchParams({
                grant_type: "password",
                client_id: clientId,
                client_secret: clientSecret,
                username: usernameorEmail,
                password,
                scope: "openid profile email",
              }),
              {
                headers: {
                  "Content-Type": "application/x-www-form-urlencoded",
                },
              }
            );

            const tokenData = tokenRes.data;

            // Fetch user info
            const userRes = await axios.get(
              keyclockEndpoints.userinfo_endpoint,
              {
                headers: {
                  Authorization: `Bearer ${tokenData.access_token}`,
                },
              }
            );

            const userData = userRes.data as TUserInfo;
            const user = await createAndSyncSession(
              ctx,
              tokenData,
              userData,
              password,
              providerId
            );

            return ctx.json({
              success: true,
              user,
              redirect: true,
              callbackURL,
            });
          } catch (error: any) {
            return ctx.error("UNAUTHORIZED", {
              message: parseKeycloakError(error),
            });
          }
        }
      ),

      // 🧾 Sign-up
      signup: createAuthEndpoint(
        "/keycloakProvider/signup",
        { method: "POST" },
        async (ctx) => {
          const {
            username,
            email,
            firstName,
            lastName,
            password,
            callbackURL,
          } = ctx.body;

          if (!username || !email || !firstName || !password) {
            return ctx.error("BAD_REQUEST", { message: "Missing credentials" });
          }

          try {
            // 1️⃣ Exchange credentials for token
            const tokenRes = await axios.post<TAuthClientToken>(
              keyclockEndpoints.token_endpoint,
              new URLSearchParams({
                client_id: clientId,
                client_secret: clientSecret,
                grant_type: "client_credentials",
              }),
              {
                headers: {
                  "Content-Type": "application/x-www-form-urlencoded",
                },
              }
            );

            const tokenClientData = tokenRes.data;

            const newUser = {
              username,
              firstName,
              lastName,
              email,
              enabled: true,
              emailVerified: false,
              credentials: [
                {
                  temporary: false,
                  type: "password",
                  value: password,
                },
              ],
            };

            // 2️⃣ create user in keycloak via Admin api
            const createUserRes = await axios.post(
              keyclockEndpoints.admin_user,
              newUser,
              {
                headers: {
                  Authorization: `Bearer ${tokenClientData.access_token}`,
                  "Content-Type": "application/json",
                },
              }
            );

            // Getting keycloak new_user id via headers
            const location = createUserRes.headers["location"];
            const keycloakUserId = location?.split("/").pop();

            // based on config args doing autosignin after user created (default true)
            if (autoSignIn) {
              // 3️⃣ Exchange credentials for user token (log in user)
              const tokenRes = await axios.post<TAuthTokenResponse>(
                keyclockEndpoints.token_endpoint,
                new URLSearchParams({
                  grant_type: "password",
                  client_id: clientId,
                  client_secret: clientSecret,
                  username,
                  password,
                  scope: "openid profile email",
                }),
                {
                  headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                  },
                }
              );

              const tokenData = tokenRes.data;

              // 4️⃣ Fetch user info using access token
              const userRes = await axios.get(
                keyclockEndpoints.userinfo_endpoint,
                {
                  headers: {
                    Authorization: `Bearer ${tokenData.access_token}`,
                  },
                }
              );

              const userData = userRes.data as TUserInfo;
              const user = await createAndSyncSession(
                ctx,
                tokenData,
                userData,
                password,
                providerId
              );

              return ctx.json({
                success: true,
                user,
                redirect: true,
                callbackURL,
              });
            }

            // Manual signup (no auto-login)
            // Sync with BetterAuth
            const user = await ctx.context.internalAdapter.createUser(
              {
                email: newUser.email,
                name: `${newUser.firstName} ${newUser.lastName}`.trim(),
                emailVerified: newUser.emailVerified,
              },
              ctx
            );

            await ctx.context.adapter.update({
              model: "user",
              where: [
                {
                  field: "email",
                  value: user.email,
                  operator: "eq",
                  connector: "AND",
                },
              ],
              update: {
                keycloakUserid: keycloakUserId,
              },
            });

            await ctx.context.internalAdapter.createAccount(
              {
                providerId,
                accountId: keycloakUserId || "dummy",
                userId: user.id,
                password: await ctx.context.password.hash(password),
              },
              ctx
            );
            return ctx.json({ success: true, redirect: false, callbackURL });
          } catch (error: any) {
            return ctx.error("BAD_REQUEST", {
              message: parseKeycloakError(error),
            });
          }
        }
      ),

      logout: createAuthEndpoint(
        "/keycloakProvider/logout",
        { method: "POST" },
        async (ctx) => {
          const { refreshToken, callbackURL } = ctx.body;

          if (!refreshToken) {
            return ctx.error("BAD_REQUEST", { message: "Missing credentials" });
          }

          try {
            await axios.post(
              keyclockEndpoints.end_session_endpoint,
              new URLSearchParams({
                client_id: clientId,
                client_secret: clientSecret,
                refresh_token: refreshToken,
              }),
              {
                headers: {
                  "Content-Type": "application/x-www-form-urlencoded",
                },
              }
            );

            const sessionCookieToken = await ctx.getSignedCookie(
              ctx.context.authCookies.sessionToken.name,
              ctx.context.secret
            );

            if (!sessionCookieToken) {
              deleteSessionCookie(ctx);
              throw new APIError("BAD_REQUEST", {
                message: "Failed to get session",
              });
            }

            ctx.context.internalAdapter.deleteSession(sessionCookieToken);
            deleteSessionCookie(ctx);
            return ctx.json({ success: true, redirect: true, callbackURL });
          } catch (e) {
            return ctx.error("BAD_REQUEST", { message: parseKeycloakError(e) });
          }
        }
      ),

      sendVerifyEmail: createAuthEndpoint(
        "/keycloakProvider/send-verify-email",
        { method: "POST" },
        async (ctx) => {
          const { keycloakUserId, userId, callbackURL } = ctx.body;

          if (!userId || !keycloakUserId) {
            return ctx.error("BAD_REQUEST", { message: "userId is required" });
          }

          const user = await ctx.context.internalAdapter.findUserById(userId);

          if (!user) {
            return ctx.error("NOT_FOUND", { message: "User not found" });
          }

          const secret = new TextEncoder().encode(ctx.context.secret);

          const token = await new SignJWT({
            keycloakUserId,
            userId,
            email: user.email,
          })
            .setProtectedHeader({ alg: "HS256" })
            .setExpirationTime("30m")
            .sign(secret);

          const verifyUrl = `${appUrl}/api/auth/keyclockProvider/email-verify?token=${token}&callbackURL=${encodeURIComponent(
            callbackURL
          )}`;

          try {
            // send mail (use your mail provider)
            const transporter = nodemailer.createTransport({
              service: "gmail",
              port: 587,
              secure: false,
              auth: {
                user: emailUser,
                pass: emailPass,
              },
            });

            await transporter.sendMail({
              from: `Bezs <${emailUser}>`,
              to: user.email,
              subject: "Verify your email",
              html: `
        <p>Click the link below to verify your email:</p>
        <a href="${verifyUrl}">${verifyUrl}</a>
      `,
            });

            return ctx.json({
              success: true,
              message: "Verification email sent",
            });
          } catch (error) {
            return ctx.error("BAD_REQUEST", {
              message: parseKeycloakError(error),
            });
          }
        }
      ),

      emailVerify: createAuthEndpoint(
        "/keycloakProvider/email-verify",
        { method: "GET" },
        async (ctx) => {
          function redirectOnError(error: string) {
            if (ctx.query?.callbackURL) {
              if (ctx.query.callbackURL.includes("?")) {
                throw ctx.redirect(`${ctx.query.callbackURL}&error=${error}`);
              }
              throw ctx.redirect(`${ctx.query.callbackURL}?error=${error}`);
            }
            throw new APIError("UNAUTHORIZED", {
              message: error,
            });
          }

          const token = ctx.query?.token;
          const callbackURL = ctx.query?.callbackURL;

          if (!token || !callbackURL) {
            return redirectOnError("Invalid token");
          }

          try {
            const secret = new TextEncoder().encode(ctx.context.secret);

            // verify token
            const { payload } = await jwtVerify(token, secret);
            const userId = payload.userId as string;
            const keycloakUserId = payload.keycloakUserId as string;

            if (!userId || !keycloakUserId) {
              return redirectOnError("invalid_payload");
            }

            // Get admin access token for Keycloak
            const tokenClientData = await getKeycloakAdminClientToken(
              keyclockEndpoints.token_endpoint,
              clientId,
              clientSecret
            );

            // update keycloak user
            const keycloakUserUpdateRes = await axios.put(
              `${keyclockEndpoints.admin_user}/${keycloakUserId}`,
              {
                emailVerified: true,
              },
              {
                headers: {
                  Authorization: `Bearer ${tokenClientData.access_token}`,
                  "Content-Type": "application/json",
                },
              }
            );

            if (keycloakUserUpdateRes.status !== 204) {
              return ctx.redirect(`${callbackURL}?verified=false`);
            }

            // update BetterAuth user
            await ctx.context.internalAdapter.updateUser(
              userId,
              {
                emailVerified: true,
              },
              ctx
            );

            // redirect on success
            return ctx.redirect(`${callbackURL}?verified=true`);
          } catch (error) {
            if (error instanceof JWTExpired) {
              return redirectOnError("token_expired");
            }
            if (error instanceof JWTInvalid) {
              return redirectOnError("invalid_token");
            }
            console.error("Email verification error:", error);
            return redirectOnError("verification_failed");
          }
        }
      ),
    },
  };
};
