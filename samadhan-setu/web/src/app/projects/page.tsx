"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { ProjectOut } from "@/types";
import { Card, Skeleton, EmptyState, Progress } from "@/components/ui/primitives";
import { listContainer, listItem, pageTransition } from "@/lib/motion";

export default function ProjectsPage() {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.projects({}),
    queryFn: async () => (await api.get<ProjectOut[]>("/projects")).data,
  });

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <h1 className="font-sora text-2xl font-bold">Projects</h1>
      {isLoading ? (
        <div className="space-y-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-20" />)}</div>
      ) : !data || data.length === 0 ? (
        <EmptyState title="No projects yet" description="Projects are created automatically once a proposal is approved." />
      ) : (
        <motion.div variants={listContainer} initial="initial" animate="animate" className="space-y-3">
          {data.map((p) => (
            <motion.div key={p.id} variants={listItem}>
              <Link href={`/projects/${p.id}`}>
                <Card hoverable>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">Project {p.id.slice(0, 8)}</span>
                    <span className="text-xs text-muted">{p.status} · {p.deployment_status}</span>
                  </div>
                  <div className="mt-2"><Progress value={p.progress_percent} /></div>
                </Card>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
