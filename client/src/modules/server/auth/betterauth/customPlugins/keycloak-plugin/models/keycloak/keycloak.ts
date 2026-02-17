export type TAuthTokenResponse = {
  access_token: string;
  expires_in: number;
  refresh_expires_in: number;
  refresh_token: string;
  token_type: string;
  "not-before-policy": number;
  session_state: string;
  scope: string;
  id_token: string;
};

export type TUserInfo = {
  sub: string;
  email_verified: boolean;
  name: string;
  preferred_username: string;
  given_name: string;
  family_name: string;
  email: string;
};

export type TAuthClientToken = Pick<
  TAuthTokenResponse,
  | "access_token"
  | "expires_in"
  | "refresh_expires_in"
  | "token_type"
  | "not-before-policy"
  | "scope"
>;
