"use client";

import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { NotificationOut } from "@/types";
import { Card, EmptyState, Skeleton } from "@/components/ui/primitives";
import { Button } from "@/components/ui/Button";
import { listContainer, listItem, pageTransition } from "@/lib/motion";

export default function NotificationsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.notifications(false),
    queryFn: async () => (await api.get<NotificationOut[]>("/notifications")).data,
  });

  const markAllRead = useMutation({
    mutationFn: async () => api.patch("/notifications/read-all"),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.notifications(false) }),
  });

  return (
    <motion.div {...pageTransition} className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="font-sora text-2xl font-bold">Notifications</h1>
        <Button variant="ghost" size="sm" onClick={() => markAllRead.mutate()}>Mark all read</Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16" />)}</div>
      ) : !data || data.length === 0 ? (
        <EmptyState title="You're all caught up" description="New updates on your challenges and projects will show up here." />
      ) : (
        <motion.div variants={listContainer} initial="initial" animate="animate" className="space-y-3">
          {data.map((n) => (
            <motion.div key={n.id} variants={listItem}>
              <Card className={n.is_read ? "opacity-70" : ""}>
                <p className="font-medium">{n.title}</p>
                <p className="text-sm text-muted">{n.body}</p>
                <p className="mt-1 text-xs text-muted">{new Date(n.created_at).toLocaleString()}</p>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
