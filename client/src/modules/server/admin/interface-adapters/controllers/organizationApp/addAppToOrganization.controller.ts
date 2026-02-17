import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { AddAppToOrganizationValidationSchema } from "../../../../../../modules/shared/schemas/admin/organizationAppValidationSchema";
import { addAppToOrganizationUseCase } from "../../../application/useCases/organizationApp/addAppToOrganization.useCase";
import { TOrganizationApp } from "../../../../../../modules/shared/entities/models/admin/organizationApp";

function presenter(organizationApp: TOrganizationApp) {
  return organizationApp;
}

export type TAddAppToOrganizationControllerOutput = ReturnType<
  typeof presenter
>;

export async function addAppToOrganizationController(
  input: any
): Promise<TAddAppToOrganizationControllerOutput> {
  const { data, error: inputParseError } =
    await AddAppToOrganizationValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organizationApp = await addAppToOrganizationUseCase(
    data.organizationId,
    data.appId
  );

  return presenter(organizationApp);
}
