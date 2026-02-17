import { TOrganizationApp } from "@/modules/shared/entities/models/admin/organizationApp";
import { getAdminInjection } from "../../../di/container";

export async function removeAppToOrganizationUseCase(
  organizationId: string,
  appId: string
): Promise<TOrganizationApp> {
  const organizationAppRepository = getAdminInjection(
    "IOrganizationAppRepository"
  );

  const organizationApp =
    await organizationAppRepository.removeAppToOrganization(
      organizationId,
      appId
    );
  return organizationApp;
}
