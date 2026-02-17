import { getAdminInjection } from "../../../di/container";

export async function getPreferenceTemplatesUseCase() {
  const preferenceTemplateRepository = getAdminInjection(
    "IPreferenceTempleteRepository"
  );
  return await preferenceTemplateRepository.getPreferenceTemplates();
}
