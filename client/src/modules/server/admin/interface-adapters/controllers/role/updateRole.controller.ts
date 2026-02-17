import { UpdateRoleValidationSchema } from "../../../../../../modules/shared/schemas/admin/roleValidationSchema";
import { updateRoleUseCase } from "../../../application/useCases/role/updateRole.useCase";
import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { TRole } from "../../../../../../modules/shared/entities/models/admin/role";

function presenter(role: TRole) {
  return role;
}

export type TUpdateRoleControllerOutput = ReturnType<typeof presenter>;

export async function updateRoleController(
  input: any
): Promise<TUpdateRoleControllerOutput> {
  const { data, error: inputParseError } =
    await UpdateRoleValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const role = await updateRoleUseCase(data);
  return presenter(role);
}
