import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { TApp } from "../../../../../shared/entities/models/admin/app";
import { updateAppUseCase } from "../../../application/useCases/app/updateAppUseCase";
import { UpdateAppValidationFormSchema } from "../../../../../../modules/shared/schemas/admin/appValidationSchema";

function presenter(app: TApp) {
  return app;
}

export type UpdateAppControllerOutputType = ReturnType<typeof presenter>;

export async function updateAppController(
  input: any
): Promise<UpdateAppControllerOutputType> {
  // TODO validate input, orchestrate use-cases
  const { data, error: inputParseError } =
    await UpdateAppValidationFormSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const app = await updateAppUseCase(data);
  return presenter(app);
}
