import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IUserRepository } from "../../user/application/repositories/userRepository.interface";
import { UserRepository } from "../../user/infrastructure/repositories/userRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IUserRepository>(DI_SYMBOLS.IUserRepository)
    .to(UserRepository)
    .inSingletonScope();
};

export const UserModule = new ContainerModule(initializeModules);
