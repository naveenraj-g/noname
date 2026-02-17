"use server";

import z from "zod";
import { createServerAction, ZSAError } from "zsa";
import { InputParseError } from "@/modules/shared/entities/errors/commonError";
import { AuthenticationError } from "@/modules/shared/entities/errors/authError";
import { send2FaOTPController } from "../../../server/auth/interface-adapters/controllers/auth/send2FaOTP.controller";
import { signOutController } from "../../../server/auth/interface-adapters/controllers/auth/signOut.controller";
import { signInWithKeycloakGenericOAuthController } from "../../../server/auth/interface-adapters/controllers/auth/signInWithKeycloakGenericOAuth.controller";
import { signInController } from "../../../server/auth/interface-adapters/controllers/auth/signIn.controller";
import { getServerSession } from "../../../server/auth/betterauth/auth-server";
import { SignUpSchema } from "@/modules/server/auth/entities/models/auth";
import { signUpController } from "@/modules/server/auth/interface-adapters/controllers/auth/signUp.controller";

const usernameOrEmailSchema = z.string().refine(
  (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const usernameRegex = /^[a-zA-Z0-9._]{3,15}$/;
    return emailRegex.test(value) || usernameRegex.test(value);
  },
  {
    message: "Enter a valid username or email",
  }
);

const signInSchema = z.object({
  usernameOrEmail: usernameOrEmailSchema,
  password: z
    .string()
    .min(8, "Password must have atleast two characters")
    .max(16, "Password must have atmost 16 characters"),
});

export const signIn = createServerAction()
  .input(signInSchema, { skipInputParsing: true })
  .handler(async ({ input }) => {
    try {
      const data = await signInController({
        usernameorEmail: input.usernameOrEmail,
        password: input.password,
      });

      return data;
    } catch (err) {
      if (err instanceof InputParseError) {
        throw new ZSAError("INPUT_PARSE_ERROR", "Invalid input");
      }

      if (err instanceof AuthenticationError) {
        throw new ZSAError("ERROR", err.message);
      }

      throw new ZSAError("ERROR", err);
    }
  });

export const signUp = createServerAction()
  .input(SignUpSchema, { skipInputParsing: true })
  .handler(async ({ input }) => {
    try {
      const data = await signUpController(input);
      return data;
    } catch (err) {
      if (err instanceof InputParseError) {
        throw new ZSAError("INPUT_PARSE_ERROR", "Invalid input");
      }

      if (err instanceof AuthenticationError) {
        throw new ZSAError("ERROR", err.message);
      }

      throw new ZSAError("ERROR", err);
    }
  });

export const signOut = createServerAction().handler(async () => {
  const session = await getServerSession();

  try {
    if (!session) {
      throw new Error("Unauthenticated");
    }

    const data = await signOutController();
    if (data.success) {
      return { success: true };
    }
  } catch (err) {
    console.log(err);
    if (err instanceof InputParseError) {
      throw new ZSAError("INPUT_PARSE_ERROR", "Invalid input");
    }

    if (err instanceof AuthenticationError) {
      throw new ZSAError("ERROR", err.message);
    }

    throw new ZSAError("ERROR", err);
  }
});

export const sendTwoFa = createServerAction().handler(async () => {
  try {
    await send2FaOTPController();
  } catch (err) {
    if (err instanceof InputParseError) {
      throw new ZSAError("INPUT_PARSE_ERROR", "Invalid input");
    }

    if (err instanceof AuthenticationError) {
      throw new ZSAError("ERROR", err.message);
    }

    throw new ZSAError("ERROR", err);
  }
});

export const signInWithKeycloakGenericOAuth = createServerAction().handler(
  async () => {
    try {
      const data = await signInWithKeycloakGenericOAuthController();
      console.log(data);
      return data;
    } catch (err) {
      if (err instanceof InputParseError) {
        throw new ZSAError("INPUT_PARSE_ERROR", "Invalid input");
      }

      if (err instanceof AuthenticationError) {
        throw new ZSAError("ERROR", err.message);
      }

      throw new ZSAError("ERROR", err);
    }
  }
);
