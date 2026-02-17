import { InputParseError } from "@/modules/shared/entities/errors/commonError";
import {
  TEmailAuthRes,
  TSignInWithEmail,
  SignInWithEmailSchema,
} from "../../../entities/models/auth";
import { getAuthInjection } from "../../../di/container";

function presenter(data: TEmailAuthRes) {
  return data;
}

export type TSignInWithEmailControllerOutput = ReturnType<typeof presenter>;

export async function signInWithEmailController(
  input: TSignInWithEmail
): Promise<TSignInWithEmailControllerOutput> {
  const authenticationService = getAuthInjection(
    "IBetterauthAuthenticationService"
  );
  const { data, error: inputParseError } =
    await SignInWithEmailSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const authData = await authenticationService.signInWithEmail(data);

  return presenter(authData);
}
