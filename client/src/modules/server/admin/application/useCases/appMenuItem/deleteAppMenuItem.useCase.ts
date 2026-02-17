import {
  TAppMenuItem,
  TDeleteAppMenuItem,
} from "@/modules/shared/entities/models/admin/appMenuItem";
import { getAdminInjection } from "../../../di/container";

export async function deleteAppMenuItemUseCase(
  data: TDeleteAppMenuItem
): Promise<TAppMenuItem> {
  const appMenuItemRepository = getAdminInjection("IAppMenuItemRepository");
  const appMenuItem = await appMenuItemRepository.deleteAppMenuItem(data);
  return appMenuItem;
}
