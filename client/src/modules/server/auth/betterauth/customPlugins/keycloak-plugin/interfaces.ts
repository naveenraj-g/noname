export interface KeycloakAuthPlugin {
  id: string;
  name: string;

  // Login: exchanges code for tokens, returns session
  authenticate(
    code: string,
    redirectUri: string
  ): Promise<{
    user: any;
    tokens: { access_token: string; refresh_token: string; id_token: string };
  }>;

  // Session: retrieves current session info
  getSession(accessToken: string): Promise<{
    user: any;
    roles: string[];
    expiresAt: number;
  }>;

  // Logout: revoke tokens and destroy session
  logout(refreshToken: string): Promise<void>;

  // Optional: refresh tokens automatically
  refresh(refreshToken: string): Promise<{
    access_token: string;
    refresh_token: string;
    id_token: string;
  }>;
}
