import {
  TMapOrUnmapAppMenuItemsToRoleInput,
  TRoleAppMenuItem,
} from "@/modules/shared/entities/models/admin/roleAppMenuItem";
import { getAdminInjection } from "../../../di/container";

export async function mapAppMenuItemsToRoleUseCase(
  input: TMapOrUnmapAppMenuItemsToRoleInput
): Promise<TRoleAppMenuItem> {
  const roleAppMenuItemRepository = getAdminInjection(
    "IRoleAppMenuItemRepository"
  );
  const roleAppMenuItems =
    await roleAppMenuItemRepository.mapAppMenuItemsToRole({
      ...input,
    });
  return roleAppMenuItems;
}
