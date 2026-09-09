"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useAuthStore } from "@/store/auth";
import { Card } from "@/components/ui/primitives";
import { pageTransition } from "@/lib/motion";

export default function ProfilePage() {
  const { user, isHydrated, hydrate } = useAuthStore();
  const router = useRouter();

  useEffect(() => { hydrate(); }, [hydrate]);
  useEffect(() => {
    if (isHydrated && !user) router.replace("/login");
  }, [isHydrated, user, router]);

  if (!user) return null;

  return (
    <motion.div {...pageTransition} className="mx-auto max-w-lg">
      <Card>
        <h1 className="font-sora text-xl font-semibold">Your profile</h1>
        <div className="mt-4 space-y-3 text-sm">
          <Row label="Name" value={user.name} />
          <Row label="Email" value={user.email} />
          <Row label="Role" value={user.role.replace(/_/g, " ")} />
          <Row label="District" value={user.district ?? "—"} />
          <Row label="Organisation" value={user.org_name ?? "—"} />
          <Row label="Member since" value={new Date(user.created_at).toLocaleDateString()} />
        </div>
      </Card>
    </motion.div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-border-light py-2 dark:border-border-dark">
      <span className="text-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
