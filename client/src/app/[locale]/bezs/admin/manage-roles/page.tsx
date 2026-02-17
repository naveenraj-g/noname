import { RolesListTable } from "@/modules/client/admin/components/tables/roles-list-table/roles-list-table";
import { getAllRolesData } from "@/modules/client/admin/server-actions/role-actions";

const ManageRolesPage = async () => {
  const [data, error] = await getAllRolesData();

  return (
    <div className="w-full">
      <RolesListTable rolesData={data} error={error} />
    </div>
  );
};

export default ManageRolesPage;
