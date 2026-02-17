import { AppsListTable } from "@/modules/client/admin/components/tables/apps-list-table/apps-list-table";
import { getAllAppsData } from "@/modules/client/admin/server-actions/app-actions";
import { getServerSession } from "@/modules/server/auth/betterauth/auth-server";

const ManageAppsPage = async () => {
  const session = await getServerSession();

  if (!session) {
    throw new Error("UNAUTHORIZED");
  }

  const [data, error] = await getAllAppsData();

  const user = {
    id: session.user.id,
    name: session.user.name,
    username: session.user.username,
    email: session.user.email,
  };

  return (
    <div className="space-y-8 mx-auto">
      <AppsListTable appDatas={data} error={error} user={user} />
    </div>
  );
};

export default ManageAppsPage;
