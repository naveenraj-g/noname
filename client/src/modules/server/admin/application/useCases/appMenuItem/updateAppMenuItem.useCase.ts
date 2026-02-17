import {
  TAppMenuItem,
  TUpdateAppMenuItem,
} from "@/modules/shared/entities/models/admin/appMenuItem";
import { getAdminInjection } from "../../../di/container";

export async function updateAppMenuItemUseCase(
  data: TUpdateAppMenuItem
): Promise<TAppMenuItem> {
  const appMenuItemRepository = getAdminInjection("IAppMenuItemRepository");
  const appMenuItem = await appMenuItemRepository.updateAppMenuItem({
    ...data,
  });
  return appMenuItem;
}
