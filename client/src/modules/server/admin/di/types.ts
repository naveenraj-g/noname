import { IAppRepository } from "../application/repositories/appRepository.interface";
import { IAppMenuItemRepository } from "../application/repositories/appMenuItemRepository.interface";
import { IOrganizationRepository } from "../application/repositories/organizationRepository.interface";
import { IRoleRepository } from "../application/repositories/roleRepository.interface";
import { IOrganizationMemberRepository } from "../application/repositories/organizationMemberRepository.interface";
import { IOrganizationAppRepository } from "../application/repositories/organizationAppRepository.interface";
import { IRoleAppMenuItemRepository } from "../application/repositories/roleAppMenuItemRepository.interface";
import { IrbacRepository } from "../application/repositories/rbacRepository.interface";
import { IPreferenceTempleteRepository } from "../application/repositories/preferenceTemplateRepository.interface";

export const DI_SYMBOLS = {
  // Repositorys
  IAppRepository: Symbol.for("IAppRepository"),
  IAppMenuItemRepository: Symbol.for("IAppMenuItemRepository"),
  IOrganizationRepository: Symbol.for("IOrganizationRepository"),
  IRoleRepository: Symbol.for("IRoleRepository"),
  IOrganizationMemberRepository: Symbol.for("IOrganizationMemberRepository"),
  IOrganizationAppRepository: Symbol.for("IOrganizationAppRepository"),
  IRoleAppMenuItemRepository: Symbol.for("IRoleAppMenuItemRepository"),
  IrbacRepository: Symbol.for("IrbacRepository"),
  IPreferenceTempleteRepository: Symbol.for("IPreferenceTempleteRepository"),
};

export interface DI_RETURN_TYPES {
  // Repositorys
  IAppRepository: IAppRepository;
  IAppMenuItemRepository: IAppMenuItemRepository;
  IOrganizationRepository: IOrganizationRepository;
  IRoleRepository: IRoleRepository;
  IOrganizationMemberRepository: IOrganizationMemberRepository;
  IOrganizationAppRepository: IOrganizationAppRepository;
  IRoleAppMenuItemRepository: IRoleAppMenuItemRepository;
  IrbacRepository: IrbacRepository;
  IPreferenceTempleteRepository: IPreferenceTempleteRepository;
}
