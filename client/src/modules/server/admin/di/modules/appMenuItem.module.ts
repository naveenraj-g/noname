import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IAppMenuItemRepository } from "../../application/repositories/appMenuItemRepository.interface";
import { AppMenuItemRepository } from "../../infrastructure/repositories/appMenuItemRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IAppMenuItemRepository>(DI_SYMBOLS.IAppMenuItemRepository)
    .to(AppMenuItemRepository)
    .inSingletonScope();
};

export const AppMenuItemModule = new ContainerModule(initializeModules);
