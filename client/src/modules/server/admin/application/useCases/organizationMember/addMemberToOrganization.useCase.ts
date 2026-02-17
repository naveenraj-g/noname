import { getSharedInjection } from "@/modules/server/shared/di/container";
import {
  TAddMemberToOrganizationUseCase,
  TOrganizationMemberAndUser,
} from "@/modules/shared/entities/models/admin/organizationMember";
import { getAdminInjection } from "../../../di/container";

export async function addMemberToOrganizationUseCase(
  data: TAddMemberToOrganizationUseCase
): Promise<TOrganizationMemberAndUser> {
  const { organizationId, emailOrUsername } = data;

  const isEmail = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(
    emailOrUsername
  );

  const email = isEmail ? emailOrUsername : undefined;
  const username = !isEmail ? emailOrUsername : undefined;

  const userRepository = getSharedInjection("IUserRepository");
  const organizationMemberRepository = getAdminInjection(
    "IOrganizationMemberRepository"
  );

  const user = await userRepository.getUserByUniqueFields({ email, username });

  if (!user) {
    throw new Error("User not found with this email or username");
  }

  const existingUser =
    await organizationMemberRepository.getMemberByUserIdAndOrganizationId(
      user.id,
      organizationId
    );

  if (existingUser) {
    throw new Error("User already exists in the organization");
  }

  const newMember = await organizationMemberRepository.addMemberToOrganization({
    organizationId,
    userId: user.id,
  });

  return newMember;
}
