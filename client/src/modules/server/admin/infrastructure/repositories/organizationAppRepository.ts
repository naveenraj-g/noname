import { OperationError } from "../../../../../modules/shared/entities/errors/commonError";
import { IOrganizationAppRepository } from "../../application/repositories/organizationAppRepository.interface";
import { prismaMain } from "../../../prisma/prisma";
import {
  OrganizationAppSchema,
  OrganizationAppsSchema,
  TOrganizationApp,
  TOrganizationApps,
} from "../../../../../modules/shared/entities/models/admin/organizationApp";
import { injectable } from "inversify";

@injectable()
export class OrganizationAppRepository implements IOrganizationAppRepository {
  constructor() {}

  async getOrganizationApps(
    organizationId: string
  ): Promise<TOrganizationApps> {
    try {
      const data = await prismaMain.appOrganization.findMany({
        where: {
          organizationId,
        },
        include: {
          app: {
            select: {
              id: true,
              name: true,
              slug: true,
              description: true,
              type: true,
            },
          },
        },
      });

      const total = await prismaMain.appOrganization.count({
        where: {
          organizationId,
        },
      });

      return await OrganizationAppsSchema.parseAsync({
        organizationApps: data,
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

  async getAppByUniqueFields(
    appId: string,
    organizationId: string
  ): Promise<TOrganizationApp | null> {
    try {
      const data = await prismaMain.appOrganization.findFirst({
        where: {
          appId,
          organizationId,
        },
        include: {
          app: {
            select: {
              id: true,
              name: true,
              slug: true,
              description: true,
              type: true,
            },
          },
        },
      });

      if (!data) {
        return null;
      }

      return await OrganizationAppSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async addAppToOrganization(
    organizationId: string,
    appId: string
  ): Promise<TOrganizationApp> {
    try {
      const data = await prismaMain.appOrganization.create({
        data: {
          organizationId,
          appId,
        },
        include: {
          app: {
            select: {
              id: true,
              name: true,
              slug: true,
              description: true,
              type: true,
            },
          },
        },
      });

      return await OrganizationAppSchema.parseAsync(data);
    } catch (error) {
      if (error instanceof Error) {
        throw new OperationError(error.message, { cause: error });
      }

      throw new OperationError("An unexpected error occurred", {
        cause: error,
      });
    }
  }

  async removeAppToOrganization(
    organizationId: string,
    appId: string
  ): Promise<TOrganizationApp> {
    try {
      const data = await prismaMain.appOrganization.delete({
        where: {
          appId_organizationId: {
            appId,
            organizationId,
          },
        },
        include: {
          app: {
            select: {
              id: true,
              name: true,
              slug: true,
              description: true,
              type: true,
            },
          },
        },
      });

      return await OrganizationAppSchema.parseAsync(data);
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
