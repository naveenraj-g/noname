import { getAdminInjection } from "../../../di/container";
import { TAppDatas } from "../../../../../shared/entities/models/admin/app";

export async function getAppsUseCase(): Promise<TAppDatas> {
  const appRepository = getAdminInjection("IAppRepository");
  const appDatas = await appRepository.getApps();
  return appDatas;
}
