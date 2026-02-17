import {
  TMapOrUnmapRbacUserOrganizationRoleInput,
  TRbac,
} from "@/modules/shared/entities/models/admin/rbac";
import { getAdminInjection } from "../../../di/container";

export async function mapRbacUserOrganizationRoleUseCase(
  input: TMapOrUnmapRbacUserOrganizationRoleInput
): Promise<TRbac> {
  const rbacRepository = getAdminInjection("IrbacRepository");

  const rbac = await rbacRepository.mapRbacUserOrganizationRole(input);

  return rbac;
}
