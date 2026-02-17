import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IRoleAppMenuItemRepository } from "../../application/repositories/roleAppMenuItemRepository.interface";
import { RoleAppMenuItemRepository } from "../../infrastructure/repositories/roleAppMenuItemRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IRoleAppMenuItemRepository>(DI_SYMBOLS.IRoleAppMenuItemRepository)
    .to(RoleAppMenuItemRepository)
    .inSingletonScope();
};

export const RoleAppMenuItemModule = new ContainerModule(initializeModules);
