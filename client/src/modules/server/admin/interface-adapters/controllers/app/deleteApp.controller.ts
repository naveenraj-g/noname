import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { TApp } from "@/modules/shared/entities/models/admin/app";
import { deleteAppUseCase } from "../../../application/useCases/app/deleteApp.useCase";
import { DeleteAppValidationSchema } from "../../../../../../modules/shared/schemas/admin/appValidationSchema";

function presenter(app: TApp) {
  return app;
}

export type DeleteAppControllerOutput = ReturnType<typeof presenter>;

export async function deleteAppController(
  input: any
): Promise<DeleteAppControllerOutput> {
  // TODO validate input, orchestrate use-cases
  const { data, error: inputParseError } =
    await DeleteAppValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const app = await deleteAppUseCase(data.id);
  return presenter(app);
}
