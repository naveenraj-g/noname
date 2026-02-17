import "reflect-metadata";
import { Container } from "inversify";
import { DI_RETURN_TYPES, DI_SYMBOLS } from "./types";
import { AuthenticationModule } from "./modules/authentication.module";

const AuthContainer = new Container({ defaultScope: "Singleton" });

const initializeContainer = () => {
  AuthContainer.load(AuthenticationModule);
};

initializeContainer();

export const getAuthInjection = <K extends keyof typeof DI_SYMBOLS>(
  symbol: K
): DI_RETURN_TYPES[K] => {
  return AuthContainer.get(DI_SYMBOLS[symbol]);
};

export { AuthContainer };

// 2:22:21
