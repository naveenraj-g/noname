import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IOrganizationRepository } from "../../application/repositories/organizationRepository.interface";
import { OrganizationRepository } from "../../infrastructure/repositories/organizationRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IOrganizationRepository>(DI_SYMBOLS.IOrganizationRepository)
    .to(OrganizationRepository)
    .inSingletonScope();
};

export const OrganizationModule = new ContainerModule(initializeModules);
