import {
  TCreateRole,
  TRole,
} from "@/modules/shared/entities/models/admin/role";
import { getAdminInjection } from "../../../di/container";

export async function createRoleUseCase(
  createData: TCreateRole
): Promise<TRole> {
  const roleRepository = getAdminInjection("IRoleRepository");

  const existingRole = await roleRepository.getRoleByUniqueField(
    createData.name
  );

  if (existingRole) {
    throw new Error("Role already exists.");
  }

  const newRole = await roleRepository.createRole({ ...createData });
  return newRole;
}
