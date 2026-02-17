import { Bind, ContainerModule } from "inversify";
import { DI_SYMBOLS } from "../types";
import { IrbacRepository } from "../../application/repositories/rbacRepository.interface";
import { RbacRepository } from "../../infrastructure/repositories/rbacRepository";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IrbacRepository>(DI_SYMBOLS.IrbacRepository)
    .to(RbacRepository)
    .inSingletonScope();
};

export const RbacModule = new ContainerModule(initializeModules);
