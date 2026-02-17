import {
  TMapOrUnmapAppMenuItemsToRoleInput,
  TRoleAppMenuItem,
} from "@/modules/shared/entities/models/admin/roleAppMenuItem";
import { getAdminInjection } from "../../../di/container";

export async function unmapAppMenuItemsToRoleUseCase(
  input: TMapOrUnmapAppMenuItemsToRoleInput
): Promise<TRoleAppMenuItem> {
  const roleAppMenuItemRepository = getAdminInjection(
    "IRoleAppMenuItemRepository"
  );
  const roleAppMenuItems =
    await roleAppMenuItemRepository.unmapAppMenuItemsToRole({
      ...input,
    });
  return roleAppMenuItems;
}
