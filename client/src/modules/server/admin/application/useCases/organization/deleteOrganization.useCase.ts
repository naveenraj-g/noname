import { TOrganization } from "@/modules/shared/entities/models/admin/organization";
import { getAdminInjection } from "../../../di/container";

export async function deleteOrganizationUseCase(
  id: string
): Promise<TOrganization> {
  const organizationRepository = await getAdminInjection(
    "IOrganizationRepository"
  );
  const organization = await organizationRepository.deleteOrganization(id);
  return organization;
}
