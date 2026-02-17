import {
  UsersListTable,
  TUser,
} from "@/modules/client/admin/components/tables/users-list-table/users-list-table";
import { auth } from "@/modules/server/auth/betterauth/auth";
import { headers } from "next/headers";

const ManageOrganizationsPage = async () => {
  const { users, total } = await auth.api.listUsers({
    query: {},
    headers: await headers(),
  });

  return (
    <div className="space-y-8 mx-auto">
      <UsersListTable usersData={users as TUser[]} total={total} />
    </div>
  );
};

export default ManageOrganizationsPage;
