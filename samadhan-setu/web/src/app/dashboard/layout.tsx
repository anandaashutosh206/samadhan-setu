"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Skeleton } from "@/components/ui/primitives";

const PATH_ROLE_MAP: Record<string, string> = {
  "/dashboard/citizen": "CITIZEN",
  "/dashboard/govt": "GOVT_OFFICIAL",
  "/dashboard/university": "UNIVERSITY_ADMIN",
  "/dashboard/industry": "INDUSTRY_PARTNER",
  "/dashboard/student": "STUDENT",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isHydrated, hydrate } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    hydrate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!isHydrated) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    const requiredRole = PATH_ROLE_MAP[pathname];
    if (requiredRole && user.role !== requiredRole && user.role !== "SUPER_ADMIN") {
      router.replace("/challenges");
    }
  }, [isHydrated, user, pathname, router]);

  if (!isHydrated || !user) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  return <>{children}</>;
}
