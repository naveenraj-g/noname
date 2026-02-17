import {
  TMapOrUnmapRbacUserOrganizationRoleInput,
  TRbac,
  TRbacDatas,
} from "@/modules/shared/entities/models/admin/rbac";

export interface IrbacRepository {
  getRbacDatas(): Promise<TRbacDatas>;
  mapRbacUserOrganizationRole(
    input: TMapOrUnmapRbacUserOrganizationRoleInput
  ): Promise<TRbac>;
  unmapRbacUserOrganizationRole(
    input: TMapOrUnmapRbacUserOrganizationRoleInput
  ): Promise<TRbac>;
}
