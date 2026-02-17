import { TRbacDatas } from "@/modules/shared/entities/models/admin/rbac";
import { getAdminInjection } from "../../../di/container";

export async function getRbacDatasUseCase(): Promise<TRbacDatas> {
  const rbacRepository = getAdminInjection("IrbacRepository");

  const rbacDatas = await rbacRepository.getRbacDatas();

  return rbacDatas;
}
