import {
  RoleSchema,
  RolesDataSchema,
  TCreateRole,
  TRole,
  TRolesData,
  TUpdateRole,
} from "../../../../../modules/shared/entities/models/admin/role";
import { IRoleRepository } from "../../application/repositories/roleRepository.interface";
import { OperationError } from "../../../../../modules/shared/entities/errors/commonError";
import { prismaMain } from "../../../prisma/prisma";
import { injectable } from "inversify";

@injectable()
export class RoleRepository implements IRoleRepository {
  constructor() {}

  async getRoles(): Promise<TRolesData> {
    try {
      const data = await prismaMain.role.findMany({
        orderBy: {
          updatedAt: "desc",
        },
      });

      const total = await prismaMain.role.count();

      return await RolesDataSchema.parseAsync({
        roleDatas: data,
        total,
      });
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async getRoleByUniqueField(roleName: string): Promise<TRole | null> {
    try {
      const data = await prismaMain.role.findUnique({
        where: {
          name: roleName,
        },
      });

      if (!data) {
        return null;
      }

      return await RoleSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async createRole(createData: TCreateRole): Promise<TRole> {
    try {
      const data = await prismaMain.role.create({
        data: {
          ...createData,
        },
      });

      return await RoleSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async updateRole(updateData: TUpdateRole): Promise<TRole> {
    const { id, ...updateValues } = updateData;

    try {
      const data = await prismaMain.role.update({
        where: {
          id,
        },
        data: {
          ...updateValues,
        },
      });

      return await RoleSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async deleteRole(roleId: string): Promise<TRole> {
    try {
      const data = await prismaMain.role.delete({
        where: {
          id: roleId,
        },
      });

      return await RoleSchema.parseAsync(data);
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
