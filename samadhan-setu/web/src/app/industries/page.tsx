"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Building2 } from "lucide-react";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { IndustryOut } from "@/types";
import { Card, Skeleton, Badge } from "@/components/ui/primitives";
import { listContainer, listItem, pageTransition } from "@/lib/motion";

export default function IndustriesPage() {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.industries({}),
    queryFn: async () => (await api.get<IndustryOut[]>("/industries")).data,
  });

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <h1 className="font-sora text-2xl font-bold">Industry & startup partners</h1>
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-40" />)}</div>
      ) : (
        <motion.div variants={listContainer} initial="initial" animate="animate" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data?.map((ind) => (
            <motion.div key={ind.id} variants={listItem}>
              <Card hoverable>
                <Building2 className="mb-2 h-5 w-5 text-secondary" />
                <p className="font-sora font-semibold">{ind.name}</p>
                <p className="text-xs text-muted">{ind.district} · {ind.type}</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {ind.capabilities.slice(0, 3).map((c) => <Badge key={c}>{c}</Badge>)}
                </div>
                {ind.csr_budget_range ? <p className="mt-2 text-xs text-muted">CSR budget: {ind.csr_budget_range}</p> : null}
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
