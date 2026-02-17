import { prismaMain } from "../../../prisma/prisma";
import { IrbacRepository } from "../../application/repositories/rbacRepository.interface";
import { OperationError } from "../../../../../modules/shared/entities/errors/commonError";
import {
  RbacDatasSchema,
  RbacSchema,
  TMapOrUnmapRbacUserOrganizationRoleInput,
  TRbac,
  TRbacDatas,
} from "../../../../../modules/shared/entities/models/admin/rbac";
import { injectable } from "inversify";

@injectable()
export class RbacRepository implements IrbacRepository {
  constructor() {}

  async getRbacDatas(): Promise<TRbacDatas> {
    try {
      const data = await prismaMain.rBAC.findMany({
        include: {
          organization: {
            select: {
              id: true,
              name: true,
            },
          },
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
          role: {
            select: {
              id: true,
              name: true,
            },
          },
        },
        orderBy: {
          createdAt: "asc",
        },
      });

      const total = await prismaMain.rBAC.count();

      return await RbacDatasSchema.parseAsync({
        rbacDatas: data,
        total,
      });
    } catch (error) {
      console.log(error);
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async mapRbacUserOrganizationRole(
    input: TMapOrUnmapRbacUserOrganizationRoleInput
  ): Promise<TRbac> {
    try {
      const data = await prismaMain.rBAC.create({
        data: {
          ...input,
        },
        include: {
          organization: {
            select: {
              id: true,
              name: true,
            },
          },
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
          role: {
            select: {
              id: true,
              name: true,
            },
          },
        },
      });

      return await RbacSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async unmapRbacUserOrganizationRole(
    input: TMapOrUnmapRbacUserOrganizationRoleInput
  ): Promise<TRbac> {
    try {
      const data = await prismaMain.rBAC.delete({
        where: {
          organizationId_userId_roleId: {
            ...input,
          },
        },
        include: {
          organization: {
            select: {
              id: true,
              name: true,
            },
          },
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              email: true,
            },
          },
          role: {
            select: {
              id: true,
              name: true,
            },
          },
        },
      });

      return await RbacSchema.parseAsync(data);
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
