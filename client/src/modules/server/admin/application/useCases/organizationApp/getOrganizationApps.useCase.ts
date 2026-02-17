import { TOrganizationApps } from "@/modules/shared/entities/models/admin/organizationApp";
import { getAdminInjection } from "../../../di/container";

export async function getOrganizationAppsUseCase(
  organizationId: string
): Promise<TOrganizationApps> {
  const organizationAppRepository = getAdminInjection(
    "IOrganizationAppRepository"
  );
  const organizationApps = await organizationAppRepository.getOrganizationApps(
    organizationId
  );
  return organizationApps;
}
