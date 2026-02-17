import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { AddAppToOrganizationValidationSchema as RemoveAppToOrganizationValidationSchema } from "../../../../../../modules/shared/schemas/admin/organizationAppValidationSchema";
import { TOrganizationApp } from "../../../../../../modules/shared/entities/models/admin/organizationApp";
import { removeAppToOrganizationUseCase } from "../../../application/useCases/organizationApp/removeAppToOrganization.useCase";

function presenter(organizationApp: TOrganizationApp) {
  return organizationApp;
}

export type TRemoveAppFromOrganizationControllerOutput = ReturnType<
  typeof presenter
>;

export async function removeAppFromOrganizationController(
  input: any
): Promise<TRemoveAppFromOrganizationControllerOutput> {
  const { data, error: inputParseError } =
    await RemoveAppToOrganizationValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organizationApp = await removeAppToOrganizationUseCase(
    data.organizationId,
    data.appId
  );

  return presenter(organizationApp);
}
