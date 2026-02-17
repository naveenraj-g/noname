import { Bind, ContainerModule } from "inversify";
import { IAppRepository } from "../../application/repositories/appRepository.interface";
import { DI_SYMBOLS } from "../types";
import { AppRepository } from "../../infrastructure/repositories/appRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IAppRepository>(DI_SYMBOLS.IAppRepository)
    .to(AppRepository)
    .inSingletonScope();
};

export const AppModule = new ContainerModule(initializeModules);
