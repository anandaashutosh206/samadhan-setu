"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import { useAuthStore } from "@/store/auth";
import type { ProposalOut } from "@/types";
import { Card, Badge, Skeleton, ErrorState } from "@/components/ui/primitives";
import { Button } from "@/components/ui/Button";
import { pageTransition } from "@/lib/motion";

export default function ProposalDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const qc = useQueryClient();

  const { data: proposal, isLoading, isError } = useQuery({
    queryKey: ["proposal", id],
    queryFn: async () => (await api.get<ProposalOut>(`/proposals/${id}`)).data,
  });

  const approveMutation = useMutation({
    mutationFn: async () => (await api.patch<ProposalOut>(`/proposals/${id}/status`, { status: "APPROVED" })).data,
    onSuccess: (data) => {
      qc.setQueryData(["proposal", id], data);
      toast.success("Proposal approved — a project has been created");
    },
    onError: () => toast.error("Only a government official can approve proposals"),
  });

  if (isLoading) return <Skeleton className="h-64" />;
  if (isError || !proposal) return <ErrorState message="Proposal not found." />;

  return (
    <motion.div {...pageTransition} className="mx-auto max-w-3xl space-y-6">
      <Card>
        <div className="mb-2 flex items-center gap-2">
          <Badge>{proposal.status}</Badge>
          <span className="text-xs text-muted">TRL {proposal.trl_level} · {proposal.timeline_weeks} weeks</span>
        </div>
        <h1 className="font-sora text-2xl font-bold">{proposal.title}</h1>

        <div className="mt-4 space-y-3 text-sm">
          <Section label="Approach" value={proposal.approach} />
          <Section label="Methodology" value={proposal.methodology} />
          <Section label="Expected outcome" value={proposal.expected_outcome} />
        </div>

        <p className="mt-4 font-mono text-sm text-primary">Budget estimate: ₹{proposal.budget_estimate.toLocaleString()}</p>

        {user?.role === "GOVT_OFFICIAL" && proposal.status === "SUBMITTED" ? (
          <Button className="mt-5" onClick={() => approveMutation.mutate()} isLoading={approveMutation.isPending}>
            Approve proposal
          </Button>
        ) : null}

        {proposal.status === "APPROVED" || proposal.status === "FUNDED" ? (
          <Button className="mt-5" variant="ghost" onClick={() => router.push("/projects")}>
            View linked project →
          </Button>
        ) : null}
      </Card>
    </motion.div>
  );
}

function Section({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-1">{value}</p>
    </div>
  );
}
