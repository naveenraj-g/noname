import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IRoleRepository } from "../../application/repositories/roleRepository.interface";
import { RoleRepository } from "../../infrastructure/repositories/roleRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IRoleRepository>(DI_SYMBOLS.IRoleRepository)
    .to(RoleRepository)
    .inSingletonScope();
};

export const RoleModule = new ContainerModule(initializeModules);
