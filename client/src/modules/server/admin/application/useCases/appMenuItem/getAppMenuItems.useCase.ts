import { getAdminInjection } from "../../../di/container";
import { TAppMenuItemsData } from "@/modules/shared/entities/models/admin/appMenuItem";

export async function getAppMenuItemsUseCase(
  appId: string
): Promise<TAppMenuItemsData> {
  const appMenuItemRepository = getAdminInjection("IAppMenuItemRepository");
  const appMenuItems = await appMenuItemRepository.getAppMenuItems(appId);
  return appMenuItems;
}
