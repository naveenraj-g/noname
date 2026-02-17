import {
  TCreateOrganization,
  TOrganization,
} from "@/modules/shared/entities/models/admin/organization";
import { getAdminInjection } from "../../../di/container";

export async function createOrganizationUseCase(
  createData: TCreateOrganization
): Promise<TOrganization> {
  const organizationRepository = getAdminInjection("IOrganizationRepository");

  const existingOrganization =
    await organizationRepository.getOrganizationByUniqueFields(
      createData.name,
      createData.slug
    );

  if (existingOrganization) {
    throw new Error("Organization already exists.");
  }

  const newOrganization = await organizationRepository.createOrganization({
    ...createData,
  });
  return newOrganization;
}
