import {
  OrganizationMemberAndUserSchema,
  OrganizationMembersAndUsersSchema,
  TAddMemberToOrganization,
  TOrganizationMemberAndUser,
  TOrganizationMembersAndUsers,
  TRemoveMemberFromOrganization,
} from "../../../../../modules/shared/entities/models/admin/organizationMember";
import { IOrganizationMemberRepository } from "../../application/repositories/organizationMemberRepository.interface";
import { OperationError } from "../../../../../modules/shared/entities/errors/commonError";
import { prismaMain } from "../../../prisma/prisma";
import { injectable } from "inversify";

@injectable()
export class OrganizationMemberRepository
  implements IOrganizationMemberRepository
{
  async getOrganizationMembers(
    organizationId: string
  ): Promise<TOrganizationMembersAndUsers> {
    try {
      const data = await prismaMain.member.findMany({
        where: {
          organizationId,
        },
        include: {
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
        },
      });

      const total = await prismaMain.member.count({
        where: {
          organizationId,
        },
      });

      const dataWithTotal = await OrganizationMembersAndUsersSchema.parseAsync({
        organizationMembersAndUsers: data,
        total,
      });

      return dataWithTotal;
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async addMemberToOrganization(
    addMemberToOrgData: TAddMemberToOrganization
  ): Promise<TOrganizationMemberAndUser> {
    const { organizationId, userId } = addMemberToOrgData;

    try {
      const data = await prismaMain.member.create({
        data: {
          organizationId,
          userId,
          role: "member",
        },
        include: {
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
        },
      });

      return await OrganizationMemberAndUserSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async addOwnerToOrganization(
    addOwnerToOrgData: TAddMemberToOrganization
  ): Promise<TOrganizationMemberAndUser> {
    const { organizationId, userId } = addOwnerToOrgData;

    try {
      const data = await prismaMain.member.create({
        data: {
          organizationId,
          userId,
          role: "owner",
        },
        include: {
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
        },
      });

      return await OrganizationMemberAndUserSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async removeMemberFromOrganization(
    removeMemberFromOrgData: TRemoveMemberFromOrganization
  ): Promise<TOrganizationMemberAndUser> {
    const { id, organizationId, userId } = removeMemberFromOrgData;

    try {
      const data = await prismaMain.member.delete({
        where: {
          id,
          organizationId,
          userId,
        },
        include: {
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
        },
      });

      return await OrganizationMemberAndUserSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async getMemberByUserIdAndOrganizationId(
    userId: string,
    organizationId: string
  ): Promise<TOrganizationMemberAndUser | null> {
    try {
      const data = await prismaMain.member.findFirst({
        where: {
          userId,
          organizationId,
        },
        include: {
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
        },
      });

      if (!data) {
        return null;
      }

      return await OrganizationMemberAndUserSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }
}
