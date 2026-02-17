import {
  TAddMemberToOrganization,
  TOrganizationMemberAndUser,
  TOrganizationMembersAndUsers,
  TRemoveMemberFromOrganization,
} from "@/modules/shared/entities/models/admin/organizationMember";

export interface IOrganizationMemberRepository {
  getOrganizationMembers(
    organizationId: string
  ): Promise<TOrganizationMembersAndUsers>;
  addOwnerToOrganization(
    addOwnerToOrgData: TAddMemberToOrganization
  ): Promise<TOrganizationMemberAndUser>;
  addMemberToOrganization(
    addMemberToOrgData: TAddMemberToOrganization
  ): Promise<TOrganizationMemberAndUser>;
  removeMemberFromOrganization(
    removeMemberFromOrgData: TRemoveMemberFromOrganization
  ): Promise<TOrganizationMemberAndUser>;
  getMemberByUserIdAndOrganizationId(
    userId: string,
    organizationId: string
  ): Promise<TOrganizationMemberAndUser | null>;
}
