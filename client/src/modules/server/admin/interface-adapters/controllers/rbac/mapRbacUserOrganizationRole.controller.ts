import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { MapOrUnMapRbacUserOrgRoleValidationSchema } from "../../../../../../modules/shared/schemas/admin/rbacValidationSchema";
import { mapRbacUserOrganizationRoleUseCase } from "../../../application/useCases/rbac/mapRbacUserOrganizationRole.useCase";
import { TRbac } from "../../../../../../modules/shared/entities/models/admin/rbac";

function presenter(rbac: TRbac) {
  return rbac;
}

export type TmapRbacUserOrganizationRoleControllerOutPut = ReturnType<
  typeof presenter
>;

export async function mapRbacUserOrganizationRoleController(
  input: any
): Promise<TmapRbacUserOrganizationRoleControllerOutPut> {
  const { data, error: inputParseError } =
    await MapOrUnMapRbacUserOrgRoleValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const rbac = await mapRbacUserOrganizationRoleUseCase(data);
  return presenter(rbac);
}
