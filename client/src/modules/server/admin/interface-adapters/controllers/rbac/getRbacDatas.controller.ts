import { TRbacDatas } from "../../../../../../modules/shared/entities/models/admin/rbac";
import { getRbacDatasUseCase } from "../../../application/useCases/rbac/getRbacDatas.useCase";

function presenter(rbacDatas: TRbacDatas) {
  return rbacDatas;
}

export type TGetRbacDatasControllerOutPut = ReturnType<typeof presenter>;

export async function getRbacDatasController(): Promise<TGetRbacDatasControllerOutPut> {
  const rbacDatas = await getRbacDatasUseCase();
  return presenter(rbacDatas);
}
