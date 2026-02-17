import { OperationError } from "../../../../../modules/shared/entities/errors/commonError";
import { IAppMenuItemRepository } from "../../application/repositories/appMenuItemRepository.interface";
import { prismaMain } from "../../../prisma/prisma";
import {
  AppMenuItemSchema,
  AppMenuItemsDataSchema,
  TAppMenuItem,
  TAppMenuItemsData,
  TCreateAppMenuItem,
  TDeleteAppMenuItem,
  TUpdateAppMenuItem,
} from "../../../../../modules/shared/entities/models/admin/appMenuItem";
import { injectable } from "inversify";

@injectable()
export class AppMenuItemRepository implements IAppMenuItemRepository {
  constructor() {}

  async getAppMenuItems(appId: string): Promise<TAppMenuItemsData> {
    try {
      const appMenuItems = await prismaMain.appMenuItem.findMany({
        where: {
          appId,
        },
        orderBy: {
          updatedAt: "desc",
        },
      });

      const total = await prismaMain.appMenuItem.count({
        where: {
          appId,
        },
      });

      const data = await AppMenuItemsDataSchema.parseAsync({
        appMenuItemsData: appMenuItems,
        total,
      });

      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async createAppMenuItem(
    createData: TCreateAppMenuItem
  ): Promise<TAppMenuItem> {
    try {
      const data = await prismaMain.appMenuItem.create({
        data: {
          ...createData,
        },
      });

      return await AppMenuItemSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async getAppByUniqueFields(
    appId: string,
    appMenuItemSlug: string
  ): Promise<TAppMenuItem | null> {
    try {
      const data = await prismaMain.appMenuItem.findFirst({
        where: {
          appId,
          slug: appMenuItemSlug,
        },
      });

      if (!data) {
        return null;
      }

      return await AppMenuItemSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async updateAppMenuItem(
    updateData: TUpdateAppMenuItem
  ): Promise<TAppMenuItem> {
    const { appId, id, ...updateValues } = updateData;

    try {
      const data = await prismaMain.appMenuItem.update({
        where: {
          id,
          appId,
        },
        data: {
          ...updateValues,
        },
      });

      return await AppMenuItemSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async deleteAppMenuItem(
    deleteData: TDeleteAppMenuItem
  ): Promise<TAppMenuItem> {
    try {
      const data = await prismaMain.appMenuItem.delete({
        where: {
          appId: deleteData.appId,
          id: deleteData.id,
        },
      });

      return await AppMenuItemSchema.parseAsync(data);
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
