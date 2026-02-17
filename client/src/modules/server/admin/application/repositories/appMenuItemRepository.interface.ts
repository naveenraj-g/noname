import {
  TAppMenuItem,
  TAppMenuItemsData,
  TCreateAppMenuItem,
  TDeleteAppMenuItem,
  TUpdateAppMenuItem,
} from "@/modules/shared/entities/models/admin/appMenuItem";

export interface IAppMenuItemRepository {
  getAppMenuItems(appId: string): Promise<TAppMenuItemsData>;
  createAppMenuItem(createData: TCreateAppMenuItem): Promise<TAppMenuItem>;
  getAppByUniqueFields(
    appId: string,
    appMenuItemSlug: string
  ): Promise<TAppMenuItem | null>;
  updateAppMenuItem(updateData: TUpdateAppMenuItem): Promise<TAppMenuItem>;
  deleteAppMenuItem(deleteData: TDeleteAppMenuItem): Promise<TAppMenuItem>;
}
