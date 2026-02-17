import axios from "axios";
import { TAuthTokenResponse, TUserInfo } from "../models/keycloak/keycloak";
import { setSessionCookie } from "better-auth/cookies";

// Utility to format errors safely
export const parseKeycloakError = (err: any): string => {
  if (axios.isAxiosError(err)) {
    return (
      err.response?.data?.error_description ||
      err.response?.data?.errorMessage ||
      err.message ||
      "Unexpected Keycloak error"
    );
  }
  return "Unexpected server error";
};

// Helper for creating sessions and syncing with BetterAuth
export const createAndSyncSession = async (
  ctx: any,
  tokenData: TAuthTokenResponse,
  userData: TUserInfo,
  password: string,
  providerId: string
) => {
  const ip =
    ctx.request?.headers.get("x-forwarded-for") ??
    ctx.request?.headers.get("cf-connecting-ip") ??
    null;
  const ua = ctx.request?.headers.get("user-agent") ?? null;

  const now = Date.now();
  const expiresAt = new Date(now + (tokenData.expires_in || 3600) * 1000);

  // Check if user exists
  const existing = await ctx.context.internalAdapter.findUserByEmail(
    userData.email,
    { includeAccounts: true }
  );

  let user;
  if (existing?.user) {
    user = await ctx.context.internalAdapter.updateUser(
      existing.user.id,
      {
        email: userData.email,
        name: userData.name,
        emailVerified: userData.email_verified,
      },
      ctx
    );
  } else {
    user = await ctx.context.internalAdapter.createUser(
      {
        email: userData.email,
        name: userData.name,
        emailVerified: userData.email_verified,
      },
      ctx
    );
  }

  // Upsert account
  const account =
    existing?.accounts.find((a: any) => a.providerId === providerId) || null;

  // console.log({ existing, account, userData });

  if (account) {
    await ctx.context.internalAdapter.updateAccount(
      account.id,
      {
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        idToken: tokenData.id_token,
        scope: tokenData.scope,
        password: await ctx.context.password.hash(password),
        accessTokenExpiresAt: new Date(
          Date.now() + tokenData.expires_in * 1000
        ),
        refreshTokenExpiresAt: new Date(
          Date.now() + tokenData.refresh_expires_in * 1000
        ),
      },
      ctx
    );
  } else {
    await ctx.context.internalAdapter.createAccount(
      {
        providerId,
        accountId: userData.sub,
        userId: user.id,
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        accessTokenExpiresAt: new Date(
          Date.now() + tokenData.expires_in * 1000
        ),
        refreshTokenExpiresAt: new Date(
          Date.now() + tokenData.refresh_expires_in * 1000
        ),
        idToken: tokenData.id_token,
        scope: tokenData.scope,
        password: await ctx.context.password.hash(password),
      },
      ctx
    );
  }

  // Create session
  const session = await ctx.context.internalAdapter.createSession(
    user.id,
    ctx,
    false,
    {
      expiresAt,
      ipAddress: ip,
      userAgent: ua,
      token: tokenData.access_token,
      userId: user.id,
    },
    false
  );

  // Set cookies
  await setSessionCookie(ctx, { session, user });
  console.log("Set Session");

  return user;
};
