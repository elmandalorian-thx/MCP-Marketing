import { AdminSidebar } from "@/components/admin-sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      <AdminSidebar />
      <div className="ml-[260px]">
        {children}
      </div>
    </div>
  );
}
