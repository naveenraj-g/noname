import "reflect-metadata";
import { Container } from "inversify";
import { DI_RETURN_TYPES, DI_SYMBOLS } from "./types";
import {
  AppMenuItemModule,
  AppModule,
  OrganizationAppModule,
  OrganizationMemberModule,
  OrganizationModule,
  PreferenceTemplateModule,
  RbacModule,
  RoleAppMenuItemModule,
  RoleModule,
} from "./modules";

const AdminContainer = new Container({ defaultScope: "Singleton" });

const initializeContainer = () => {
  AdminContainer.load(AppModule);
  AdminContainer.load(AppMenuItemModule);
  AdminContainer.load(OrganizationModule);
  AdminContainer.load(RoleModule);
  AdminContainer.load(OrganizationMemberModule);
  AdminContainer.load(OrganizationAppModule);
  AdminContainer.load(RoleAppMenuItemModule);
  AdminContainer.load(RbacModule);
  AdminContainer.load(PreferenceTemplateModule);
};

initializeContainer();

export const getAdminInjection = <K extends keyof typeof DI_SYMBOLS>(
  symbol: K
): DI_RETURN_TYPES[K] => {
  return AdminContainer.get(DI_SYMBOLS[symbol]);
};

export { AdminContainer };
