import { InputParseError } from "@/modules/shared/entities/errors/commonError";
import { SignUpSchema, TSignUp } from "../../../entities/models/auth";
import { getAuthInjection } from "../../../di/container";

export async function signUpController(input: TSignUp) {
  const betterAuthAuthenticationService = getAuthInjection(
    "IBetterauthAuthenticationService"
  );

  const parsed = await SignUpSchema.safeParseAsync(input);

  if (parsed.error && !parsed.success) {
    throw new InputParseError(parsed.error.name, { cause: parsed.error });
  }

  const data = await betterAuthAuthenticationService.signUp({
    ...parsed.data,
  });
  return data;
}
