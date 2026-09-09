"use client";

import { useParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { MilestoneOut, ProjectOut } from "@/types";
import { Card, Skeleton, ErrorState } from "@/components/ui/primitives";
import { LifecycleStepper, MilestoneKanban } from "@/components/ProjectLifecycle";
import { pageTransition } from "@/lib/motion";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();

  const { data: project, isLoading, isError } = useQuery({
    queryKey: queryKeys.project(id),
    queryFn: async () => (await api.get<ProjectOut>(`/projects/${id}`)).data,
  });

  const { data: milestones } = useQuery({
    queryKey: queryKeys.milestones(id),
    queryFn: async () => (await api.get<MilestoneOut[]>(`/projects/${id}/milestones`)).data,
    enabled: !!project,
  });

  const handleStatusChange = async (milestoneId: string, status: string) => {
    await api.patch(`/projects/milestones/${milestoneId}/status`, { status });
    qc.invalidateQueries({ queryKey: queryKeys.milestones(id) });
  };

  if (isLoading) return <Skeleton className="h-64" />;
  if (isError || !project) return <ErrorState message="Project not found." />;

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <h1 className="font-sora text-2xl font-bold">Project lifecycle</h1>

      <Card>
        <LifecycleStepper status={project.deployment_status} progress={project.progress_percent} />
      </Card>

      <Card>
        <h2 className="mb-4 font-sora font-semibold">Milestones</h2>
        {milestones && milestones.length > 0 ? (
          <MilestoneKanban milestones={milestones} onStatusChange={handleStatusChange} />
        ) : (
          <p className="text-sm text-muted">No milestones added yet.</p>
        )}
      </Card>

      {Object.keys(project.impact_metrics ?? {}).length > 0 ? (
        <Card>
          <h2 className="mb-3 font-sora font-semibold">Impact metrics</h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {Object.entries(project.impact_metrics).map(([k, v]) => (
              <div key={k} className="rounded-xl bg-primary-soft p-3 text-center">
                <p className="font-mono text-lg font-bold text-primary">{String(v)}</p>
                <p className="mt-1 text-xs text-muted">{k.replace(/_/g, " ")}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </motion.div>
  );
}
