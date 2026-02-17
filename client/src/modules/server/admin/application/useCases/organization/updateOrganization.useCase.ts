import {
  TOrganization,
  TUpdateOrganization,
} from "@/modules/shared/entities/models/admin/organization";
import { getAdminInjection } from "../../../di/container";

export async function updateOrganizationUseCase(
  updateData: TUpdateOrganization
): Promise<TOrganization> {
  const organizationRepository = getAdminInjection("IOrganizationRepository");
  const organization = await organizationRepository.updateOrganization({
    ...updateData,
  });
  return organization;
}
