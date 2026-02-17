import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { RemoveMemberFromOrganizationValidationSchema } from "../../../../../../modules/shared/schemas/admin/organizationMemberValidationSchema";
import { removeMemberFromOrganizationUseCase } from "../../../application/useCases/organizationMember/removeMemberFromOrganization.useCase";
import { TOrganizationMemberAndUser } from "../../../../../../modules/shared/entities/models/admin/organizationMember";

function presenter(organizationMember: TOrganizationMemberAndUser) {
  return organizationMember;
}

export type TRemoveMemberFromOrganizationControllerOutput = ReturnType<
  typeof presenter
>;

export async function removeMemberFromOrganizationController(
  input: any
): Promise<TRemoveMemberFromOrganizationControllerOutput> {
  const { data, error: inputParseError } =
    await RemoveMemberFromOrganizationValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organizationMember = await removeMemberFromOrganizationUseCase(data);
  return presenter(organizationMember);
}
