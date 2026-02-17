import {
  TGetRoleAppMenuItemsInput,
  TMapOrUnmapAppMenuItemsToRoleInput,
  TRoleAppMenuItem,
  TRoleAppMenuItemsData,
} from "@/modules/shared/entities/models/admin/roleAppMenuItem";

export interface IRoleAppMenuItemRepository {
  getRoleAppMenuItems(
    input: TGetRoleAppMenuItemsInput
  ): Promise<TRoleAppMenuItemsData>;
  mapAppMenuItemsToRole(
    input: TMapOrUnmapAppMenuItemsToRoleInput
  ): Promise<TRoleAppMenuItem>;
  unmapAppMenuItemsToRole(
    input: TMapOrUnmapAppMenuItemsToRoleInput
  ): Promise<TRoleAppMenuItem>;
}
