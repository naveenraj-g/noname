import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IOrganizationAppRepository } from "../../application/repositories/organizationAppRepository.interface";
import { OrganizationAppRepository } from "../../infrastructure/repositories/organizationAppRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IOrganizationAppRepository>(DI_SYMBOLS.IOrganizationAppRepository)
    .to(OrganizationAppRepository)
    .inSingletonScope();
};

export const OrganizationAppModule = new ContainerModule(initializeModules);
