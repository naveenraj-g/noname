import {
  twoFactorClient,
  customSessionClient,
  usernameClient,
  genericOAuthClient,
  oidcClient,
  adminClient,
  organizationClient,
  inferAdditionalFields,
} from "better-auth/client/plugins";
import { createAuthClient } from "better-auth/react";
import { auth } from "../../../server/auth/betterauth/auth";

export const authClient = createAuthClient({
  baseURL: process.env.BETTER_AUTH_URL,
  plugins: [
    twoFactorClient(),
    adminClient(),
    usernameClient(),
    organizationClient(),
    customSessionClient(),
    genericOAuthClient(),
    oidcClient(),
    inferAdditionalFields<typeof auth>(),
  ],
});

export const { useSession } = authClient;
