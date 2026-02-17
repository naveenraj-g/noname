import { buttonVariants } from "@/components/ui/button";
import Link from "next/link";

const AdminPage = async () => {
  return (
    <div>
      <div>
        <h1 className="text-2xl font-semibold">Admin Dashboard</h1>
        <p>Manage Users</p>
      </div>
      <Link
        className={buttonVariants({ variant: "link", size: "sm" })}
        href="/bezs/admin/manage-apps"
      >
        Manage Apps
      </Link>
    </div>
  );
};

export default AdminPage;
