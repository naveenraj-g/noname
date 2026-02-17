import { AdminModalProvider } from "@/modules/client/admin/providers/admin-modal-provider";

const AdminLayout = async ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="w-full">
      <AdminModalProvider />
      {children}
    </div>
  );
};

export default AdminLayout;
