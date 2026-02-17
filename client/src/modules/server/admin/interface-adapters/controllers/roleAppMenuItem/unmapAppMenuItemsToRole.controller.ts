import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { MapOrUnmapAppMenuItemToRoleValidateSchema } from "../../../../../../modules/shared/schemas/admin/roleAppMenuItemValidatorSchema";
import { TRoleAppMenuItem } from "../../../../../../modules/shared/entities/models/admin/roleAppMenuItem";
import { unmapAppMenuItemsToRoleUseCase } from "../../../application/useCases/roleAppMenuItem/unmapAppMenuItemsToRole.useCase";

function presenter(roleAppMenuItem: TRoleAppMenuItem) {
  return roleAppMenuItem;
}

export type TUnMapAppMenuItemsToRoleControllerOutput = ReturnType<
  typeof presenter
>;

export async function unmapAppMenuItemsToRoleController(
  input: any
): Promise<TUnMapAppMenuItemsToRoleControllerOutput> {
  const { data, error: inputParseError } =
    await MapOrUnmapAppMenuItemToRoleValidateSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const roleAppMenuItem = await unmapAppMenuItemsToRoleUseCase({ ...data });
  return presenter(roleAppMenuItem);
}
