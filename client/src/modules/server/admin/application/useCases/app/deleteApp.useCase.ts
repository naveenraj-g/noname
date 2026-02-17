import { getAdminInjection } from "../../../di/container";
import { TApp } from "../../../../../shared/entities/models/admin/app";

export async function deleteAppUseCase(appId: string): Promise<TApp> {
  const appRepository = getAdminInjection("IAppRepository");
  const app = await appRepository.deleteApp(appId);
  return app;
}
