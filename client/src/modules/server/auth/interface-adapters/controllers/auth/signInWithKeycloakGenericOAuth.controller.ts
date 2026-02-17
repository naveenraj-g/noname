import { TSignInWithKeycloakGenericOAuth } from "../../../entities/models/auth";
import { getAuthInjection } from "../../../di/container";
import { getAuthProvider } from "@/modules/server/auth/utils/getAuthProvider";

function presenter(data: TSignInWithKeycloakGenericOAuth) {
  return data;
}

export type TSignInWithKeycloakControllerOutput = ReturnType<typeof presenter>;

export async function signInWithKeycloakGenericOAuthController(): Promise<TSignInWithKeycloakControllerOutput> {
  const keycloakAuthenticationService = getAuthInjection(
    "IKeycloakAuthenticationService"
  );

  const { isKeycloak } = getAuthProvider();

  let data: TSignInWithKeycloakGenericOAuth = {
    redirect: false,
    url: "",
  };

  if (isKeycloak) {
    data = await keycloakAuthenticationService.signInWithKeycloakGenericOAuth();
  }

  return presenter(data);
}
