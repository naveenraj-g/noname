import { TOrganizationMembersAndUsers } from "@/modules/shared/entities/models/admin/organizationMember";
import { getAdminInjection } from "../../../di/container";

export async function getOrganizationMembersUseCase(
  organizationId: string
): Promise<TOrganizationMembersAndUsers> {
  const organizationMemberRepository = getAdminInjection(
    "IOrganizationMemberRepository"
  );
  const organizationMembers =
    await organizationMemberRepository.getOrganizationMembers(organizationId);
  return organizationMembers;
}
