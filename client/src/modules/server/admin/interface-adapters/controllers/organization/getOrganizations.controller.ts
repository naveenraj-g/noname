import { TOrganizationsData } from "../../../../../../modules/shared/entities/models/admin/organization";
import { getOrganizationsUseCase } from "../../../application/useCases/organization/getOrganizations.useCase";

function presenter(organizationDatas: TOrganizationsData) {
  return organizationDatas;
}

export type TGetOrganizationsControllerOutput = ReturnType<typeof presenter>;

export async function getOrganizationsController(): Promise<TGetOrganizationsControllerOutput> {
  const organizationDatas = await getOrganizationsUseCase();
  return presenter(organizationDatas);
}
