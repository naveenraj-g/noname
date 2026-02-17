import { TRole } from "@/modules/shared/entities/models/admin/role";
import { getAdminInjection } from "../../../di/container";

export async function deleteRoleUseCase(roleId: string): Promise<TRole> {
  const roleRepository = getAdminInjection("IRoleRepository");
  const role = await roleRepository.deleteRole(roleId);
  return role;
}
