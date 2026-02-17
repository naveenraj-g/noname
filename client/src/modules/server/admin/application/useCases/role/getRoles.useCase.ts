import { TRolesData } from "@/modules/shared/entities/models/admin/role";
import { getAdminInjection } from "../../../di/container";

export async function getRolesUseCase(): Promise<TRolesData> {
  const roleRepository = getAdminInjection("IRoleRepository");
  const roles = await roleRepository.getRoles();
  return roles;
}
