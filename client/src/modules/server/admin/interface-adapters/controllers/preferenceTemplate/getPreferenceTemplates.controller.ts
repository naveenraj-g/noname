import { TPreferenceTemplates } from "../../../../../../modules/shared/entities/models/admin/preferenceTemplete";
import { getPreferenceTemplatesUseCase } from "../../../application/useCases/preferenceTemplete/getPreferenceTemplates.useCase";

function presenter(preferenceTemplates: TPreferenceTemplates) {
  return preferenceTemplates;
}

export type TGetPreferenceTemplatesControllerOutput = ReturnType<
  typeof presenter
>;

export async function getPreferenceTemplatesController(): Promise<TGetPreferenceTemplatesControllerOutput> {
  const preferenceTemplates = await getPreferenceTemplatesUseCase();
  return presenter(preferenceTemplates);
}
