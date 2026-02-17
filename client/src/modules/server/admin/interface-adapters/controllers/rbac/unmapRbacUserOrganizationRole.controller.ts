import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { MapOrUnMapRbacUserOrgRoleValidationSchema } from "../../../../../../modules/shared/schemas/admin/rbacValidationSchema";
import { TRbac } from "../../../../../../modules/shared/entities/models/admin/rbac";
import { unmapRbacUserOrganizationRoleUseCase } from "../../../application/useCases/rbac/unmapRbacUserOrganizationRole.useCase";

function presenter(rbac: TRbac) {
  return rbac;
}

export type TUnMapRbacUserOrganizationRoleControllerOutPut = ReturnType<
  typeof presenter
>;

export async function unmapRbacUserOrganizationRoleController(
  input: any
): Promise<TUnMapRbacUserOrganizationRoleControllerOutPut> {
  const { data, error: inputParseError } =
    await MapOrUnMapRbacUserOrgRoleValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const rbac = await unmapRbacUserOrganizationRoleUseCase(data);
  return presenter(rbac);
}
