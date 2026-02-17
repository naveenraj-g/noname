import { InputParseError } from "../../../../../../modules/shared/entities/errors/commonError";
import { GetOrganizationAppsValidationSchema } from "../../../../../../modules/shared/schemas/admin/organizationAppValidationSchema";
import { getOrganizationAppsUseCase } from "../../../application/useCases/organizationApp/getOrganizationApps.useCase";
import { TOrganizationApps } from "../../../../../../modules/shared/entities/models/admin/organizationApp";

function presenter(organizationApps: TOrganizationApps) {
  return organizationApps;
}

export type TGetOrganizationAppsControllerOutput = ReturnType<typeof presenter>;

export async function getOrganizationAppsController(
  input: any
): Promise<TGetOrganizationAppsControllerOutput> {
  const { data, error: inputParseError } =
    await GetOrganizationAppsValidationSchema.safeParseAsync(input);

  if (inputParseError) {
    throw new InputParseError(inputParseError.name, { cause: inputParseError });
  }

  const organizationApps = await getOrganizationAppsUseCase(
    data.organizationId
  );

  return presenter(organizationApps);
}
