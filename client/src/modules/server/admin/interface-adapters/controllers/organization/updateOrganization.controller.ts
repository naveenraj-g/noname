import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { UpdateOrganizationFormSchema } from "../../../../../../modules/shared/schemas/admin/organizationValidationSchema";
import { updateOrganizationUseCase } from "../../../application/useCases/organization/updateOrganization.useCase";
import { TOrganization } from "../../../../../../modules/shared/entities/models/admin/organization";

function presenter(organization: TOrganization) {
  return organization;
}

export type TUpdateOrganizationControllerOutput = ReturnType<typeof presenter>;

export async function updateOrganizationController(
  input: any
): Promise<TUpdateOrganizationControllerOutput> {
  const { data, error: inputParseError } =
    await UpdateOrganizationFormSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organization = await updateOrganizationUseCase(data);
  return presenter(organization);
}
