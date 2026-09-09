"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { ProposalOut } from "@/types";
import { Card, Skeleton, EmptyState, Badge } from "@/components/ui/primitives";
import { listContainer, listItem, pageTransition } from "@/lib/motion";

export default function ProposalsPage() {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.proposals({}),
    queryFn: async () => (await api.get<ProposalOut[]>("/proposals")).data,
  });

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <h1 className="font-sora text-2xl font-bold">Proposals</h1>
      {isLoading ? (
        <div className="space-y-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24" />)}</div>
      ) : !data || data.length === 0 ? (
        <EmptyState title="No proposals yet" description="Universities submit solution proposals once a challenge is routed to them." />
      ) : (
        <motion.div variants={listContainer} initial="initial" animate="animate" className="space-y-3">
          {data.map((p) => (
            <motion.div key={p.id} variants={listItem}>
              <Link href={`/proposals/${p.id}`}>
                <Card hoverable className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-sora font-semibold">{p.title}</p>
                    <p className="mt-1 line-clamp-1 text-sm text-muted">{p.approach}</p>
                  </div>
                  <div className="flex flex-shrink-0 items-center gap-3">
                    <Badge>{p.status}</Badge>
                    <span className="font-mono text-xs text-muted">₹{p.budget_estimate.toLocaleString()}</span>
                  </div>
                </Card>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
