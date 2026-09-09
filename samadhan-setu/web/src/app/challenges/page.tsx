"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Plus } from "lucide-react";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { ChallengeListOut, Domain } from "@/types";
import { ChallengeCard } from "@/components/ChallengeCard";
import { Button } from "@/components/ui/Button";
import { Input, Select, Skeleton, EmptyState, ErrorState } from "@/components/ui/primitives";
import { listContainer, listItem, pageTransition } from "@/lib/motion";

const DOMAINS: Domain[] = [
  "education", "agriculture", "healthcare", "water_resources", "environment",
  "energy", "urban_development", "accessibility", "public_administration", "rural_livelihoods",
];

export default function ChallengesPage() {
  const [q, setQ] = useState("");
  const [domain, setDomain] = useState("");
  const [sort, setSort] = useState("recent");
  const [page, setPage] = useState(1);

  const filters = { q, domain, sort, page, page_size: 12 };
  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.challenges(filters),
    queryFn: async () =>
      (
        await api.get<ChallengeListOut>("/challenges", {
          params: { q: q || undefined, domain: domain || undefined, sort, page, page_size: 12 },
        })
      ).data,
  });

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-sora text-2xl font-bold">Challenges</h1>
        <Link href="/challenges/new">
          <Button><Plus className="h-4 w-4" /> Report a challenge</Button>
        </Link>
      </div>

      <div className="flex flex-wrap gap-3">
        <Input
          placeholder="Search challenges..."
          value={q}
          onChange={(e) => { setPage(1); setQ(e.target.value); }}
          className="max-w-xs"
        />
        <Select value={domain} onChange={(e) => { setPage(1); setDomain(e.target.value); }} className="max-w-xs">
          <option value="">All domains</option>
          {DOMAINS.map((d) => <option key={d} value={d}>{d.replace(/_/g, " ")}</option>)}
        </Select>
        <Select value={sort} onChange={(e) => setSort(e.target.value)} className="max-w-xs">
          <option value="recent">Most recent</option>
          <option value="priority">Highest priority</option>
          <option value="upvotes">Most upvoted</option>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-48" />)}
        </div>
      ) : isError ? (
        <ErrorState message="Couldn't load challenges. Please try again." />
      ) : !data || data.items.length === 0 ? (
        <EmptyState title="No challenges found" description="Try a different search or be the first to report one." />
      ) : (
        <>
          <motion.div variants={listContainer} initial="initial" animate="animate" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((c) => (
              <motion.div key={c.id} variants={listItem}>
                <ChallengeCard challenge={c} />
              </motion.div>
            ))}
          </motion.div>

          {data.pages > 1 ? (
            <div className="flex items-center justify-center gap-3 pt-2">
              <Button variant="ghost" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
              <span className="text-sm text-muted">Page {data.page} of {data.pages}</span>
              <Button variant="ghost" size="sm" disabled={page >= data.pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
            </div>
          ) : null}
        </>
      )}
    </motion.div>
  );
}
