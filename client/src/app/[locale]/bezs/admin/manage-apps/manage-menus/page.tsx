import { AppMenuItemsListTable } from "@/modules/client/admin/components/tables/app-menuItems-list-table/app-menuItems-list-table";
import { getAppMenuItems } from "@/modules/client/admin/server-actions/appMenutem-actions";

const AppMenuItemsPage = async ({
  searchParams,
}: {
  searchParams?: { appId: string };
}) => {
  const appId = (await searchParams)?.appId;

  if (!appId) {
    throw new Error("Failed to get appId");
  }

  const [data, error] = await getAppMenuItems({ appId });

  return (
    <div className="mx-auto">
      <AppMenuItemsListTable
        appMenuItemDatas={data}
        appId={appId}
        error={error}
      />
    </div>
  );
};

export default AppMenuItemsPage;
