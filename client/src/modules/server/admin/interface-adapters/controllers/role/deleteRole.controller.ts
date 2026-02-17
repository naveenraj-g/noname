import { DeleteRoleValidationSchema } from "../../../../../../modules/shared/schemas/admin/roleValidationSchema";
import { deleteRoleUseCase } from "../../../application/useCases/role/deleteRole.useCase";
import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { TRole } from "../../../../../../modules/shared/entities/models/admin/role";

function presenter(role: TRole) {
  return role;
}

export type TDeleteRoleControllerOutput = ReturnType<typeof presenter>;

export async function deleteRoleController(
  input: any
): Promise<TDeleteRoleControllerOutput> {
  const { data, error: inputParseError } =
    await DeleteRoleValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const role = await deleteRoleUseCase(data.id);
  return presenter(role);
}
