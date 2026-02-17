import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { MapOrUnmapAppMenuItemToRoleValidateSchema } from "../../../../../../modules/shared/schemas/admin/roleAppMenuItemValidatorSchema";
import { mapAppMenuItemsToRoleUseCase } from "../../../application/useCases/roleAppMenuItem/mapAppMenuItemsToRole.useCase";
import { TRoleAppMenuItem } from "../../../../../../modules/shared/entities/models/admin/roleAppMenuItem";

function presenter(roleAppMenuItem: TRoleAppMenuItem) {
  return roleAppMenuItem;
}

export type TMapAppMenuItemsToRoleControllerOutput = ReturnType<
  typeof presenter
>;

export async function mapAppMenuItemsToRoleController(
  input: any
): Promise<TMapAppMenuItemsToRoleControllerOutput> {
  const { data, error: inputParseError } =
    await MapOrUnmapAppMenuItemToRoleValidateSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const roleAppMenuItem = await mapAppMenuItemsToRoleUseCase({ ...data });
  return presenter(roleAppMenuItem);
}
