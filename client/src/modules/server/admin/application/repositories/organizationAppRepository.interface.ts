import {
  TOrganizationApp,
  TOrganizationApps,
} from "@/modules/shared/entities/models/admin/organizationApp";

export interface IOrganizationAppRepository {
  getOrganizationApps(organizationId: string): Promise<TOrganizationApps>;
  addAppToOrganization(
    organizationId: string,
    appId: string
  ): Promise<TOrganizationApp>;
  removeAppToOrganization(
    organizationId: string,
    appId: string
  ): Promise<TOrganizationApp>;
  getAppByUniqueFields(
    appId: string,
    organizationId: string
  ): Promise<TOrganizationApp | null>;
}
