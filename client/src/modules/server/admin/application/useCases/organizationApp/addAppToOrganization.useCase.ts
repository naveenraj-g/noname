import { TOrganizationApp } from "@/modules/shared/entities/models/admin/organizationApp";
import { getAdminInjection } from "../../../di/container";

export async function addAppToOrganizationUseCase(
  organizationId: string,
  appId: string
): Promise<TOrganizationApp> {
  const organizationAppRepository = getAdminInjection(
    "IOrganizationAppRepository"
  );

  const existingApp = await organizationAppRepository.getAppByUniqueFields(
    appId,
    organizationId
  );

  if (existingApp) {
    throw new Error("App already exists in the organization");
  }

  const organizationApp = await organizationAppRepository.addAppToOrganization(
    organizationId,
    appId
  );
  return organizationApp;
}
