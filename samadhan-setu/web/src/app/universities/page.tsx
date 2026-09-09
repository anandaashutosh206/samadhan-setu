"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { GraduationCap } from "lucide-react";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { UniversityOut } from "@/types";
import { Card, Skeleton, Badge } from "@/components/ui/primitives";
import { listContainer, listItem, pageTransition } from "@/lib/motion";

export default function UniversitiesPage() {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.universities({}),
    queryFn: async () => (await api.get<UniversityOut[]>("/universities")).data,
  });

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <h1 className="font-sora text-2xl font-bold">Partner universities</h1>
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-40" />)}</div>
      ) : (
        <motion.div variants={listContainer} initial="initial" animate="animate" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data?.map((u) => (
            <motion.div key={u.id} variants={listItem}>
              <Card hoverable>
                <GraduationCap className="mb-2 h-5 w-5 text-primary" />
                <p className="font-sora font-semibold">{u.name}</p>
                <p className="text-xs text-muted">{u.district} · {u.type}</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {u.disciplines.slice(0, 3).map((d) => <Badge key={d}>{d}</Badge>)}
                </div>
                <div className="mt-3 flex items-center justify-between text-xs text-muted">
                  <span>{u.has_incubation ? "Has incubation centre" : "No incubation centre"}</span>
                  {u.naac_grade ? <span>NAAC {u.naac_grade}</span> : null}
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
