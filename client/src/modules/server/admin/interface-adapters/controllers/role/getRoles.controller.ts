import { TRolesData } from "../../../../../../modules/shared/entities/models/admin/role";
import { getRolesUseCase } from "../../../application/useCases/role/getRoles.useCase";

function presenter(roleDatas: TRolesData) {
  return roleDatas;
}

export type TGetRolesControllerOutput = ReturnType<typeof presenter>;

export async function getRolesController(): Promise<TGetRolesControllerOutput> {
  const roleDatas = await getRolesUseCase();
  return presenter(roleDatas);
}
