import {
  TCreatePreferenceTemplate,
  TPreferenceTemplate,
  TPreferenceTemplates,
} from "@/modules/shared/entities/models/admin/preferenceTemplete";

export interface IPreferenceTempleteRepository {
  getPreferenceTemplates(): Promise<TPreferenceTemplates>;
  getPreferenceByScopeDefaultField(): Promise<TPreferenceTemplate | null>;
  createPreferenceTemplate(
    createData: TCreatePreferenceTemplate
  ): Promise<TPreferenceTemplate>;
  updatePreferenceTemplate(
    fields: TPreferenceTemplate
  ): Promise<TPreferenceTemplate>;
  deletePreferenceTemplate(id: string): Promise<TPreferenceTemplate>;
}
