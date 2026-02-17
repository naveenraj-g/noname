import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { UpdateAppMenuItemValidationSchema } from "../../../../../../modules/shared/schemas/admin/appMenuItemValidationSchema";
import { updateAppMenuItemUseCase } from "../../../application/useCases/appMenuItem/updateAppMenuItem.useCase";
import { TAppMenuItem } from "../../../../../../modules/shared/entities/models/admin/appMenuItem";

function presenter(appMenuItem: TAppMenuItem) {
  return appMenuItem;
}

export type TUpdateAppMenuItemControllerOutput = ReturnType<typeof presenter>;

export async function updateAppMenuItemController(
  input: any
): Promise<TUpdateAppMenuItemControllerOutput> {
  const { data, error: inputParseError } =
    await UpdateAppMenuItemValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const appMenuItem = await updateAppMenuItemUseCase(data);
  return presenter(appMenuItem);
}
