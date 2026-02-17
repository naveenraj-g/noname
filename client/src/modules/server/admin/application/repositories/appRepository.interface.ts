import {
  TApp,
  TAppDatas,
  TCreateApp,
  TUpdateApp,
} from "../../../../shared/entities/models/admin/app";

export interface IAppRepository {
  getApps(): Promise<TAppDatas>;
  getAppById(appId: string): Promise<TApp>;
  getAppByUniqueFields(appName: string, appSlug: string): Promise<TApp | null>;
  createApp(app: TCreateApp): Promise<TApp>;
  updateApp(app: TUpdateApp): Promise<TApp>;
  deleteApp(appId: string): Promise<TApp>;
}
