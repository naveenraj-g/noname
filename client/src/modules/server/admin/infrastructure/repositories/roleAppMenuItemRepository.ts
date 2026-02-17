import {
  RoleAppMenuItemSchema,
  RoleAppMenuItemsDataSchema,
  TGetRoleAppMenuItemsInput,
  TMapOrUnmapAppMenuItemsToRoleInput,
  TRoleAppMenuItem,
  TRoleAppMenuItemsData,
} from "../../../../../modules/shared/entities/models/admin/roleAppMenuItem";
import { IRoleAppMenuItemRepository } from "../../application/repositories/roleAppMenuItemRepository.interface";
import { OperationError } from "../../../../../modules/shared/entities/errors/commonError";
import { prismaMain } from "../../../prisma/prisma";
import { injectable } from "inversify";

@injectable()
export class RoleAppMenuItemRepository implements IRoleAppMenuItemRepository {
  constructor() {}

  async getRoleAppMenuItems(
    input: TGetRoleAppMenuItemsInput
  ): Promise<TRoleAppMenuItemsData> {
    try {
      const data = await prismaMain.menuPermission.findMany({
        where: {
          ...input,
        },
      });

      return await RoleAppMenuItemsDataSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async mapAppMenuItemsToRole(
    input: TMapOrUnmapAppMenuItemsToRoleInput
  ): Promise<TRoleAppMenuItem> {
    try {
      const data = await prismaMain.menuPermission.create({
        data: {
          ...input,
        },
      });

      return await RoleAppMenuItemSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async unmapAppMenuItemsToRole(
    input: TMapOrUnmapAppMenuItemsToRoleInput
  ): Promise<TRoleAppMenuItem> {
    try {
      const data = await prismaMain.menuPermission.delete({
        where: {
          roleId_appId_appMenuItemId: {
            ...input,
          },
        },
      });

      return await RoleAppMenuItemSchema.parseAsync(data);
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
