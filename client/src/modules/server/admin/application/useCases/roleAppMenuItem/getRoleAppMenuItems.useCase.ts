import {
  TGetRoleAppMenuItemsInput,
  TRoleAppMenuItemsData,
} from "@/modules/shared/entities/models/admin/roleAppMenuItem";
import { getAdminInjection } from "../../../di/container";

export async function getRoleAppMenuItemsUseCase(
  input: TGetRoleAppMenuItemsInput
): Promise<TRoleAppMenuItemsData> {
  const roleAppMenuItemRepository = getAdminInjection(
    "IRoleAppMenuItemRepository"
  );
  const roleAppMenuItems = await roleAppMenuItemRepository.getRoleAppMenuItems({
    ...input,
  });
  return roleAppMenuItems;
}
