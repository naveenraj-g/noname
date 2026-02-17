import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { GetOrganizationMembersValidationSchema } from "../../../../../../modules/shared/schemas/admin/organizationMemberValidationSchema";
import { getOrganizationMembersUseCase } from "../../../application/useCases/organizationMember/getOrganizationMembers.useCase";
import { TOrganizationMembersAndUsers } from "../../../../../../modules/shared/entities/models/admin/organizationMember";

function presenter(organizationMembers: TOrganizationMembersAndUsers) {
  return organizationMembers;
}

export type TGetOrganizationMembersControllerOutput = ReturnType<
  typeof presenter
>;

export async function getOrganizationMembersController(
  input: any
): Promise<TGetOrganizationMembersControllerOutput> {
  const { data, error: inputParseError } =
    await GetOrganizationMembersValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organizationMembers = await getOrganizationMembersUseCase(
    data.organizationId
  );
  return presenter(organizationMembers);
}
