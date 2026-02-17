import {
  TOrganizationMemberAndUser,
  TRemoveMemberFromOrganization,
} from "@/modules/shared/entities/models/admin/organizationMember";
import { getAdminInjection } from "../../../di/container";

export async function removeMemberFromOrganizationUseCase(
  removeMemberFromOrgData: TRemoveMemberFromOrganization
): Promise<TOrganizationMemberAndUser> {
  const organizationMemberRepository = getAdminInjection(
    "IOrganizationMemberRepository"
  );
  const organizationMenber =
    await organizationMemberRepository.removeMemberFromOrganization({
      ...removeMemberFromOrgData,
    });
  return organizationMenber;
}
