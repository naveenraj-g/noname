import { getAdminInjection } from "../../../di/container";
import {
  TApp,
  TCreateApp,
} from "../../../../../shared/entities/models/admin/app";

export async function createAppUseCase(app: TCreateApp): Promise<TApp> {
  const appRepository = getAdminInjection("IAppRepository");

  const existingApp = await appRepository.getAppByUniqueFields(
    app.name,
    app.slug
  );

  if (existingApp) {
    throw new Error(`App already exists.`);
  }

  const newApp = await appRepository.createApp(app);
  return newApp;
}
