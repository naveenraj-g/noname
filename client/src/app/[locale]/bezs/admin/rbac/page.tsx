import { RBACOrgUserRoleMap } from "@/modules/client/admin/components/rbac/rbac-org-user-role-map";
import { RBACListTable } from "@/modules/client/admin/components/tables/rbac-list-table/rbac-list-table";
import { getAllOrganizationsData } from "@/modules/client/admin/server-actions/organization-actions";
import { getRbacDatas } from "@/modules/client/admin/server-actions/rbac-actions";
import { getAllRolesData } from "@/modules/client/admin/server-actions/role-actions";
import { getTranslations } from "next-intl/server";

const RBACPage = async () => {
  const t = await getTranslations("admin.rbac");

  const [allOrgsData] = await getAllOrganizationsData();
  const [allRolesData] = await getAllRolesData();
  const [data, error] = await getRbacDatas();

  return (
    <div className="space-y-8 w-full">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="text-sm">{t("subtitle")}</p>
      </div>
      <div className="space-y-16">
        <RBACOrgUserRoleMap
          allOrgs={allOrgsData?.organizationsData}
          allRoles={allRolesData?.roleDatas}
        />
        <RBACListTable
          error={error}
          rbacDatas={data}
          roleDatas={allRolesData?.roleDatas}
        />
      </div>
    </div>
  );
};

export default RBACPage;
