import { T2Fa } from "../../../entities/models/auth";
import { getAuthInjection } from "../../../di/container";

function presenter(data: T2Fa) {
  return data;
}

export type Tsend2FaOTPControllerOutput = ReturnType<typeof presenter>;

export async function send2FaOTPController(): Promise<Tsend2FaOTPControllerOutput> {
  const authenticationService = getAuthInjection(
    "IBetterauthAuthenticationService"
  );

  const data = await authenticationService.send2FaOTP();

  return presenter(data);
}
