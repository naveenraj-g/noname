import { InputParseError } from "@/modules/shared/entities/errors/commonError";
import { SignInSchema, TSignIn } from "../../../entities/models/auth";
import { getAuthInjection } from "../../../di/container";
import z from "zod";

export async function signInController(input: TSignIn) {
  const betterAuthAuthenticationService = getAuthInjection(
    "IBetterauthAuthenticationService"
  );

  const parsed = await SignInSchema.safeParseAsync(input);

  if (parsed.error && !parsed.success) {
    throw new InputParseError(parsed.error.name, { cause: parsed.error });
  }

  const { usernameorEmail, password } = parsed.data;

  const isEmailLogin = z.string().email().safeParse(usernameorEmail).success;

  if (isEmailLogin) {
    const data = await betterAuthAuthenticationService.signInWithEmail({
      email: usernameorEmail,
      password: password,
    });
    return data;
  } else {
    const data = await betterAuthAuthenticationService.signInWithUsername({
      username: usernameorEmail,
      password: password,
    });
    return data;
  }
}
