import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IOrganizationMemberRepository } from "../../application/repositories/organizationMemberRepository.interface";
import { OrganizationMemberRepository } from "../../infrastructure/repositories/organizationMemberRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IOrganizationMemberRepository>(DI_SYMBOLS.IOrganizationMemberRepository)
    .to(OrganizationMemberRepository)
    .inSingletonScope();
};

export const OrganizationMemberModule = new ContainerModule(initializeModules);
