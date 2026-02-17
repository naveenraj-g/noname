import { InputParseError } from "@/modules/shared/entities/errors/commonError";
import {
  TSignInWithUsername,
  SignInWithUsernameSchema,
  TAuthUsernameSuccessRes,
} from "../../../entities/models/auth";
import { getAuthInjection } from "../../../di/container";

function presenter(data: TAuthUsernameSuccessRes | null) {
  return data;
}

export type TSignInWithUsernameControllerOutput = ReturnType<typeof presenter>;

export async function signInWithUsernameController(
  input: TSignInWithUsername
): Promise<TSignInWithUsernameControllerOutput> {
  const authenticationService = getAuthInjection(
    "IBetterauthAuthenticationService"
  );
  const { data, error: inputParseError } =
    await SignInWithUsernameSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const authData = await authenticationService.signInWithUsername(data);

  return presenter(authData);
}
