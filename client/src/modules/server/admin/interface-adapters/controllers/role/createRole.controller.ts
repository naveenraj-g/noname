import { CreateRoleValidationSchema } from "../../../../../../modules/shared/schemas/admin/roleValidationSchema";
import { createRoleUseCase } from "../../../application/useCases/role/createRole.useCase";
import { TRole } from "../../../../../../modules/shared/entities/models/admin/role";
import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";

function presenter(role: TRole) {
  return role;
}

export type TCreateRoleControllerOutput = ReturnType<typeof presenter>;

export async function createRoleController(
  input: any
): Promise<TCreateRoleControllerOutput> {
  const { data, error: inputParseError } =
    await CreateRoleValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const role = await createRoleUseCase(data);
  return presenter(role);
}
