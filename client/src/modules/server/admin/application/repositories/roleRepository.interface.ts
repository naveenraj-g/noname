import {
  TCreateRole,
  TRole,
  TRolesData,
  TUpdateRole,
} from "@/modules/shared/entities/models/admin/role";

export interface IRoleRepository {
  getRoles(): Promise<TRolesData>;
  getRoleByUniqueField(roleName: string): Promise<TRole | null>;
  createRole(createData: TCreateRole): Promise<TRole>;
  updateRole(updateData: TUpdateRole): Promise<TRole>;
  deleteRole(roleId: string): Promise<TRole>;
}
