import { prismaMain } from "../../../prisma/prisma";
import { IAppRepository } from "../../application/repositories/appRepository.interface";
import { OperationError } from "../../../../../modules/shared/entities/errors/commonError";
import {
  AppDatasSchema,
  AppSchema,
  TApp,
  TAppDatas,
  TCreateApp,
  TUpdateApp,
} from "../../../../../modules/shared/entities/models/admin/app";
import { injectable } from "inversify";

@injectable()
export class AppRepository implements IAppRepository {
  constructor() {}

  async getApps(): Promise<TAppDatas> {
    try {
      const appDatas = await prismaMain.app.findMany({
        include: {
          _count: {
            select: {
              appMenuItems: true,
              appActions: true,
            },
          },
        },
        orderBy: {
          updatedAt: "desc",
        },
      });

      const total = await prismaMain.app.count();

      return await AppDatasSchema.parseAsync({
        appDatas,
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

  async getAppById(appId: string): Promise<TApp> {
    try {
      const data = await prismaMain.app.findUnique({
        where: {
          id: appId,
        },
      });

      return await AppSchema.parseAsync(data);
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
    appName: string,
    appSlug: string
  ): Promise<TApp | null> {
    try {
      const data = await prismaMain.app.findFirst({
        where: {
          OR: [{ name: appName }, { slug: appSlug }],
        },
      });

      if (!data) {
        return null;
      }

      return await AppSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async createApp(app: TCreateApp) {
    try {
      const data = await prismaMain.app.create({
        data: {
          ...app,
        },
      });

      return await AppSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async updateApp(app: TUpdateApp): Promise<TApp> {
    const { id, ...appDatas } = app;

    try {
      const data = await prismaMain.app.update({
        where: {
          id,
        },
        data: {
          ...appDatas,
        },
      });

      return await AppSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async deleteApp(appId: string): Promise<TApp> {
    try {
      const data = await prismaMain.app.delete({
        where: {
          id: appId,
        },
      });

      return await AppSchema.parseAsync(data);
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
