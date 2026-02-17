import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { getAppMenuItemsUseCase } from "../../../application/useCases/appMenuItem/getAppMenuItems.useCase";
import {
  AppIdSchema,
  TAppMenuItemsData,
} from "../../../../../../modules/shared/entities/models/admin/appMenuItem";

function presenter(appMenuItem: TAppMenuItemsData) {
  return appMenuItem;
}

export type getAppMenuItemsControllerOutputType = ReturnType<typeof presenter>;

export async function getAppMenuItemsController(
  input: any
): Promise<getAppMenuItemsControllerOutputType> {
  const { data, error: inputParseError } = await AppIdSchema.safeParseAsync(
    input
  );

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const appMenuItems = await getAppMenuItemsUseCase(data.appId);
  return presenter(appMenuItems);
}
