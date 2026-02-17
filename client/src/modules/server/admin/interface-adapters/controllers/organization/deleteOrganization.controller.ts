import { DeleteOrganizationFormSchema } from "../../../../../../modules/shared/schemas/admin/organizationValidationSchema";
import { deleteOrganizationUseCase } from "../../../application/useCases/organization/deleteOrganization.useCase";
import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { TOrganization } from "../../../../../../modules/shared/entities/models/admin/organization";

function presenter(organization: TOrganization) {
  return organization;
}

export type TDeleteOrganizationControllerOutput = ReturnType<typeof presenter>;

export async function deleteOrganizationController(
  input: any
): Promise<TDeleteOrganizationControllerOutput> {
  const { data, error: inputParseError } =
    await DeleteOrganizationFormSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organization = await deleteOrganizationUseCase(data.id);
  return presenter(organization);
}
