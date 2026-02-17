import { OrganizationsListTable } from "@/modules/client/admin/components/tables/organizations-list-table/organizations-list-table";
import { getAllOrganizationsData } from "@/modules/client/admin/server-actions/organization-actions";

const ManageOrganizationsPage = async () => {
  const [data, error] = await getAllOrganizationsData();

  return (
    <div className="space-y-8 mx-auto">
      <OrganizationsListTable organizationsDatas={data} error={error} />
    </div>
  );
};

export default ManageOrganizationsPage;
