import {
  TCreateOrganization,
  TOrganization,
  TOrganizationsData,
  TUpdateOrganization,
} from "@/modules/shared/entities/models/admin/organization";

export interface IOrganizationRepository {
  getOrganizations(): Promise<TOrganizationsData>;
  getOrganizationByUniqueFields(
    name: string,
    slug: string
  ): Promise<TOrganization | null>;
  createOrganization(createData: TCreateOrganization): Promise<TOrganization>;
  updateOrganization(updateData: TUpdateOrganization): Promise<TOrganization>;
  deleteOrganization(id: string): Promise<TOrganization>;
}
