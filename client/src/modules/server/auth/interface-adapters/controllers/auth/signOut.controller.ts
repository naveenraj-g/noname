import { getAuthInjection } from "../../../di/container";
import { TSuccessRes } from "../../../entities/models/auth";

export async function signOutController(): Promise<TSuccessRes> {
  const betterAuthAuthenticationService = getAuthInjection(
    "IBetterauthAuthenticationService"
  );

  const data = await betterAuthAuthenticationService.signOut();
  return data;
}
