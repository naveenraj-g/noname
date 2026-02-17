import { TOrganizationsData } from "@/modules/shared/entities/models/admin/organization";
import { getAdminInjection } from "../../../di/container";

export async function getOrganizationsUseCase(): Promise<TOrganizationsData> {
  const organizationRepository = getAdminInjection("IOrganizationRepository");
  const organizations = await organizationRepository.getOrganizations();
  return organizations;
}
