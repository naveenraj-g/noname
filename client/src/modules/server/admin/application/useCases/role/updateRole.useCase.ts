import {
  TRole,
  TUpdateRole,
} from "@/modules/shared/entities/models/admin/role";
import { getAdminInjection } from "../../../di/container";

export async function updateRoleUseCase(
  updateData: TUpdateRole
): Promise<TRole> {
  const roleRepository = getAdminInjection("IRoleRepository");
  const role = await roleRepository.updateRole({ ...updateData });
  return role;
}
