import {
  TResetPassword,
  TSignInWithEmail,
  TSignInWithUsername,
  TSignUp,
  T2Fa,
  TUpdatePassword,
  TSuccessRes,
  TSignInKeycloak,
  TSignIn,
  TSignOutKeycloak,
  TAuthEmailSuccessRes,
  TAuthUsernameSuccessRes,
  TSignInWithKeycloakGenericOAuth,
} from "../../entities/models/auth";

export interface IAuthenticationService {
  signInWithProvider(provider: string): Promise<void>;
  signInWithEmail(data: TSignInWithEmail): Promise<TAuthEmailSuccessRes>;
  signInWithUsername(
    data: TSignInWithUsername
  ): Promise<TAuthUsernameSuccessRes | null>;
  signUp(data: TSignUp): Promise<{ success: boolean; redirectUrl: string }>;
  signOut(): Promise<TSuccessRes>;
  resetPassword(data: TResetPassword): Promise<void>;
  requestPasswordReset(data: TResetPassword): Promise<void>;
  updatePassword(data: TUpdatePassword): Promise<void>;
  send2FaOTP(): Promise<T2Fa>;
}

export interface IKeycloakAuthenticationService {
  signIn(data: TSignIn): Promise<TSignInKeycloak>;
  signInWithKeycloakGenericOAuth(): Promise<TSignInWithKeycloakGenericOAuth>;
  signUp(data: TSignUp): Promise<TSignInKeycloak>;
  signOut(refreshToken: string): Promise<TSignOutKeycloak>;
  signOutWithKeycloakGenericOAuth(refreshToken: string): Promise<TSuccessRes>;
  resetPassword(data: TResetPassword): Promise<void>;
  requestPasswordReset(data: TResetPassword): Promise<void>;
  updatePassword(data: TUpdatePassword): Promise<void>;
  send2FaOTP(): Promise<T2Fa>;
}
