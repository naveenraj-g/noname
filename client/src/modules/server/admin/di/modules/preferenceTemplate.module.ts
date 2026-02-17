import { Bind, ContainerModule } from "inversify";
import { IPreferenceTempleteRepository } from "../../application/repositories/preferenceTemplateRepository.interface";
import { PreferenceTemplateRepository } from "../../infrastructure/repositories/preferenceTemplateRepository";
import { DI_SYMBOLS } from "../types";

const initializeModules = ({ bind }: { bind: Bind }) => {
  bind<IPreferenceTempleteRepository>(DI_SYMBOLS.IPreferenceTempleteRepository)
    .to(PreferenceTemplateRepository)
    .inSingletonScope();
};

export const PreferenceTemplateModule = new ContainerModule(initializeModules);
