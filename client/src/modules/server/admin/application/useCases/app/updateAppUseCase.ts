import { getAdminInjection } from "../../../di/container";
import {
  TApp,
  TUpdateApp,
} from "../../../../../shared/entities/models/admin/app";

export async function updateAppUseCase(appData: TUpdateApp): Promise<TApp> {
  const appRepository = getAdminInjection("IAppRepository");
  const app = await appRepository.updateApp(appData);
  return app;
}
