import { DeleteAppMenuItemValidationSchema } from "../../../../../../modules/shared/schemas/admin/appMenuItemValidationSchema";
import { deleteAppMenuItemUseCase } from "../../../application/useCases/appMenuItem/deleteAppMenuItem.useCase";
import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { TAppMenuItem } from "../../../../../../modules/shared/entities/models/admin/appMenuItem";

function presenter(appMenuItem: TAppMenuItem) {
  return appMenuItem;
}

export type TDeleteAppMenuItemControllerOutputType = ReturnType<
  typeof presenter
>;

export async function deleteAppMenuItemController(input: any) {
  const { data, error: inputParseError } =
    await DeleteAppMenuItemValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const appMenuItem = await deleteAppMenuItemUseCase(data);
  return presenter(appMenuItem);
}
