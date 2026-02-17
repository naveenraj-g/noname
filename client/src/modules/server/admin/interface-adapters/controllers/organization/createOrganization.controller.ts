import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { CreateOrganizationFormSchema } from "../../../../../../modules/shared/schemas/admin/organizationValidationSchema";
import { createOrganizationUseCase } from "../../../application/useCases/organization/createOrganization.useCase";
import { TOrganization } from "../../../../../../modules/shared/entities/models/admin/organization";

function presenter(organization: TOrganization) {
  return organization;
}

export type TCreateOrganizationControllerOutput = ReturnType<typeof presenter>;

export async function createOrganizationController(
  input: any
): Promise<TCreateOrganizationControllerOutput> {
  const { data, error: inputParseError } =
    await CreateOrganizationFormSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organization = await createOrganizationUseCase(data);
  return presenter(organization);
}
