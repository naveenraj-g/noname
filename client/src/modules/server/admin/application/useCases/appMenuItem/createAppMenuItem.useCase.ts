import {
  TAppMenuItem,
  TCreateAppMenuItem,
} from "@/modules/shared/entities/models/admin/appMenuItem";
import { getAdminInjection } from "../../../di/container";

export async function createAppMenuItemUseCase(
  app: TCreateAppMenuItem
): Promise<TAppMenuItem> {
  const appMenuItemRepository = getAdminInjection("IAppMenuItemRepository");

  const existingAppMenuItem = await appMenuItemRepository.getAppByUniqueFields(
    app.appId,
    app.slug
  );

  if (existingAppMenuItem) {
    throw new Error("App Menu Item already exists.");
  }

  const newApp = await appMenuItemRepository.createAppMenuItem({ ...app });
  return newApp;
}
