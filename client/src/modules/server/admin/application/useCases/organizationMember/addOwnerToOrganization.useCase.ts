import {
  TAddMemberToOrganization,
  TOrganizationMemberAndUser,
} from "@/modules/shared/entities/models/admin/organizationMember";
import { getAdminInjection } from "../../../di/container";

export async function addOwnerToOrganizationUseCase(
  addOwnerToOrgData: TAddMemberToOrganization
): Promise<TOrganizationMemberAndUser> {
  const organizationMemberRepository = getAdminInjection(
    "IOrganizationMemberRepository"
  );
  const organizationMenber =
    await organizationMemberRepository.addOwnerToOrganization({
      ...addOwnerToOrgData,
    });
  return organizationMenber;
}
