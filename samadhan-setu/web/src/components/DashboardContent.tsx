"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import { useAuthStore } from "@/store/auth";
import type { ChallengeListOut, NotificationOut, ProposalOut, Role } from "@/types";
import { Card, Skeleton, EmptyState, Badge } from "@/components/ui/primitives";
import { ChallengeCard } from "@/components/ChallengeCard";
import { pageTransition, listContainer, listItem } from "@/lib/motion";

const roleCopy: Record<Role, { title: string; description: string }> = {
  CITIZEN: { title: "Citizen dashboard", description: "Track the challenges you've reported and their progress." },
  COMMUNITY_ORG: { title: "Community org dashboard", description: "Monitor challenges reported by your community." },
  UNIVERSITY_ADMIN: { title: "University dashboard", description: "Review routed challenges and manage your proposals." },
  FACULTY_MENTOR: { title: "Faculty mentor dashboard", description: "Track proposals and projects you're mentoring." },
  STUDENT: { title: "Student dashboard", description: "See the projects your team is working on." },
  INDUSTRY_PARTNER: { title: "Industry dashboard", description: "Discover proposals ready for funding, mentorship, or pilots." },
  GOVT_OFFICIAL: { title: "Government dashboard", description: "Validate challenges and track district-wide outcomes." },
  SUPER_ADMIN: { title: "Admin dashboard", description: "Full platform oversight." },
};

export function DashboardContent({ expectedRole }: { expectedRole: Role }) {
  const user = useAuthStore((s) => s.user);
  const copy = roleCopy[expectedRole];

  const { data: myChallenges, isLoading: loadingChallenges } = useQuery({
    queryKey: queryKeys.challenges({ mine: true }),
    queryFn: async () => (await api.get<ChallengeListOut>("/challenges", { params: { page_size: 6, sort: "recent" } })).data,
  });

  const { data: proposals } = useQuery({
    queryKey: queryKeys.proposals({ dashboard: true }),
    queryFn: async () => (await api.get<ProposalOut[]>("/proposals")).data,
    enabled: expectedRole !== "CITIZEN",
  });

  const { data: notifications } = useQuery({
    queryKey: queryKeys.notifications(true),
    queryFn: async () => (await api.get<NotificationOut[]>("/notifications", { params: { unread_only: true } })).data,
  });

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <div>
        <h1 className="font-sora text-2xl font-bold">{copy.title}</h1>
        <p className="mt-1 text-sm text-muted">{copy.description}{user ? ` Welcome back, ${user.name}.` : ""}</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <h2 className="mb-3 font-sora font-semibold">Recent challenges</h2>
          {loadingChallenges ? (
            <Skeleton className="h-40" />
          ) : !myChallenges || myChallenges.items.length === 0 ? (
            <EmptyState title="Nothing here yet" description="New activity will show up as challenges move through the pipeline." />
          ) : (
            <motion.div variants={listContainer} initial="initial" animate="animate" className="grid gap-3 sm:grid-cols-2">
              {myChallenges.items.slice(0, 4).map((c) => (
                <motion.div key={c.id} variants={listItem}><ChallengeCard challenge={c} /></motion.div>
              ))}
            </motion.div>
          )}
        </Card>

        <div className="space-y-4">
          <Card>
            <h2 className="mb-3 font-sora font-semibold">Unread notifications</h2>
            {notifications && notifications.length > 0 ? (
              <div className="space-y-2">
                {notifications.slice(0, 4).map((n) => (
                  <div key={n.id} className="rounded-lg bg-black/5 p-2 text-xs dark:bg-white/5">{n.title}</div>
                ))}
                <Link href="/notifications" className="block text-xs text-primary">View all →</Link>
              </div>
            ) : (
              <p className="text-sm text-muted">You're all caught up.</p>
            )}
          </Card>

          {expectedRole !== "CITIZEN" ? (
            <Card>
              <h2 className="mb-3 font-sora font-semibold">Proposals</h2>
              {proposals && proposals.length > 0 ? (
                <div className="space-y-2">
                  {proposals.slice(0, 4).map((p) => (
                    <Link key={p.id} href={`/proposals/${p.id}`} className="flex items-center justify-between rounded-lg bg-black/5 p-2 text-xs dark:bg-white/5">
                      <span className="truncate">{p.title}</span>
                      <Badge>{p.status}</Badge>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted">No proposals yet.</p>
              )}
            </Card>
          ) : null}
        </div>
      </div>
    </motion.div>
  );
}
