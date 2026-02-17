import {
  TCreatePreferenceTemplate,
  TPreferenceTemplate,
} from "@/modules/shared/entities/models/admin/preferenceTemplete";
import { getAdminInjection } from "../../../di/container";

export async function createPreferenceTemplateUseCase(
  createData: TCreatePreferenceTemplate
): Promise<TPreferenceTemplate> {
  const preferenceTemplateRepository = getAdminInjection(
    "IPreferenceTempleteRepository"
  );

  if (createData.scope === "GLOBAL") {
    const preferenceTemplate =
      await preferenceTemplateRepository.getPreferenceByScopeDefaultField();

    if (preferenceTemplate) {
      throw new Error("Global Scope preference template already exists.");
    }
  }

  return await preferenceTemplateRepository.createPreferenceTemplate({
    ...createData,
  });
}
