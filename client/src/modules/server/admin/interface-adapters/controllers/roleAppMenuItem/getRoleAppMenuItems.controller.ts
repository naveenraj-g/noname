import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { getRoleAppMenuItemsValidateSchema } from "../../../../../../modules/shared/schemas/admin/roleAppMenuItemValidatorSchema";
import { getRoleAppMenuItemsUseCase } from "../../../application/useCases/roleAppMenuItem/getRoleAppMenuItems.useCase";
import { TRoleAppMenuItemsData } from "../../../../../../modules/shared/entities/models/admin/roleAppMenuItem";

function presenter(roleAppMenuItems: TRoleAppMenuItemsData) {
  return roleAppMenuItems;
}

export type TGetRoleAppMenuItemsControllerOutput = ReturnType<typeof presenter>;

export async function getRoleAppMenuItemsController(
  input: any
): Promise<TGetRoleAppMenuItemsControllerOutput> {
  const { data, error: inputParseError } =
    await getRoleAppMenuItemsValidateSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const roleAppMenuItems = await getRoleAppMenuItemsUseCase({ ...data });
  return presenter(roleAppMenuItems);
}
