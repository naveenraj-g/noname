import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { TApp } from "../../../../../shared/entities/models/admin/app";
import { createAppUseCase } from "../../../application/useCases/app/createApp.useCase";
import { CreateAppValidationSchema } from "../../../../../../modules/shared/schemas/admin/appValidationSchema";

function presenter(app: TApp) {
  return app;
}

export type TCreateAppControllerOutput = ReturnType<typeof presenter>;

export async function createAppController(
  input: any
): Promise<TCreateAppControllerOutput> {
  // TODO validate input, orchestrate use-cases
  const { data, error: inputParseError } =
    await CreateAppValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const app = await createAppUseCase(data);
  return presenter(app);
}
