import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { AddMemberToOrganizationValidationSchema } from "../../../../../../modules/shared/schemas/admin/organizationMemberValidationSchema";
import { addMemberToOrganizationUseCase } from "../../../application/useCases/organizationMember/addMemberToOrganization.useCase";
import { TOrganizationMemberAndUser } from "../../../../../../modules/shared/entities/models/admin/organizationMember";

function presenter(organizationMember: TOrganizationMemberAndUser) {
  return organizationMember;
}

export type TAddMemberToOrganizationControllerOutput = ReturnType<
  typeof presenter
>;

export async function addMemberToOrganizationController(
  input: any
): Promise<TAddMemberToOrganizationControllerOutput> {
  const { data, error: inputParseError } =
    await AddMemberToOrganizationValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organizationMember = await addMemberToOrganizationUseCase(data);
  return presenter(organizationMember);
}
