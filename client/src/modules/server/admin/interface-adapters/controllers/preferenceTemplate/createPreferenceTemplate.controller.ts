import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { PreferenceTemplateValidationSchema } from "../../../../../../modules/shared/schemas/admin/preferenceTemplateValidationSchema";
import { createPreferenceTemplateUseCase } from "../../../application/useCases/preferenceTemplete/createPreferenceTemplate.useCase";

function presenter(preferenceTemplate: any) {
  return preferenceTemplate;
}

export type TCreatePreferenceTemplateControllerOutput = ReturnType<
  typeof presenter
>;

export async function createPreferenceTemplateController(
  input: any
): Promise<TCreatePreferenceTemplateControllerOutput> {
  const { data, error: inputParseError } =
    await PreferenceTemplateValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const preferenceTemplate = await createPreferenceTemplateUseCase(data);
  return presenter(preferenceTemplate);
}
