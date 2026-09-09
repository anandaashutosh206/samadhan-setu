"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Download } from "lucide-react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis,
  LineChart, Line, CartesianGrid, Legend,
} from "recharts";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type {
  AnalyticsOverview, DomainCount, DistrictCount, FunnelStage, TimeseriesPoint, LeaderboardEntry, OutcomesSummary,
} from "@/types";
import { Card, Skeleton } from "@/components/ui/primitives";
import { Button } from "@/components/ui/Button";
import { pageTransition } from "@/lib/motion";

const domainColors: Record<string, string> = {
  agriculture: "#16A34A", healthcare: "#DC2626", water_resources: "#0EA5E9", education: "#4F46E5",
  energy: "#F59E0B", environment: "#14B8A6", urban_development: "#8B5CF6", accessibility: "#EC4899",
  public_administration: "#64748B", rural_livelihoods: "#D97706",
};

export default function AnalyticsPage() {
  const overview = useQuery({ queryKey: queryKeys.analyticsOverview, queryFn: async () => (await api.get<AnalyticsOverview>("/analytics/overview")).data });
  const byDomain = useQuery({ queryKey: queryKeys.analyticsByDomain, queryFn: async () => (await api.get<DomainCount[]>("/analytics/by-domain")).data });
  const byDistrict = useQuery({ queryKey: queryKeys.analyticsByDistrict, queryFn: async () => (await api.get<DistrictCount[]>("/analytics/by-district")).data });
  const funnel = useQuery({ queryKey: queryKeys.analyticsFunnel, queryFn: async () => (await api.get<FunnelStage[]>("/analytics/funnel")).data });
  const timeseries = useQuery({ queryKey: queryKeys.analyticsTimeseries, queryFn: async () => (await api.get<TimeseriesPoint[]>("/analytics/timeseries")).data });
  const leaderboard = useQuery({ queryKey: queryKeys.analyticsLeaderboard, queryFn: async () => (await api.get<LeaderboardEntry[]>("/analytics/leaderboard")).data });
  const outcomes = useQuery({ queryKey: queryKeys.analyticsOutcomes, queryFn: async () => (await api.get<OutcomesSummary>("/analytics/outcomes")).data });

  return (
    <motion.div {...pageTransition} className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-sora text-2xl font-bold">Analytics</h1>
        <a href={`${process.env.NEXT_PUBLIC_API_URL}/reports/analytics.pdf`} target="_blank" rel="noreferrer">
          <Button variant="ghost" size="sm"><Download className="h-4 w-4" /> Export PDF</Button>
        </a>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total challenges", value: overview.data?.total_challenges },
          { label: "Universities", value: overview.data?.total_universities },
          { label: "Proposals", value: overview.data?.total_proposals },
          { label: "Beneficiaries reached", value: overview.data?.total_beneficiaries },
        ].map((s) => (
          <Card key={s.label} className="text-center">
            <p className="font-mono text-2xl font-bold text-primary">{overview.isLoading ? "—" : s.value}</p>
            <p className="mt-1 text-xs text-muted">{s.label}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 font-sora font-semibold">Challenges by domain</h2>
          {byDomain.isLoading ? <Skeleton className="h-64" /> : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={byDomain.data} dataKey="count" nameKey="domain" innerRadius={60} outerRadius={95} paddingAngle={2}>
                  {byDomain.data?.map((d) => <Cell key={d.domain} fill={domainColors[d.domain] ?? "#64748B"} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <h2 className="mb-3 font-sora font-semibold">Funnel: challenge lifecycle</h2>
          {funnel.isLoading ? <Skeleton className="h-64" /> : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={funnel.data} layout="vertical" margin={{ left: 24 }}>
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="stage" width={90} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#4F46E5" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <h2 className="mb-3 font-sora font-semibold">Submissions vs resolutions (6 months)</h2>
          {timeseries.isLoading ? <Skeleton className="h-64" /> : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={timeseries.data}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="submitted" stroke="#4F46E5" strokeWidth={2} />
                <Line type="monotone" dataKey="resolved" stroke="#0D9488" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <h2 className="mb-3 font-sora font-semibold">Challenges by district</h2>
          {byDistrict.isLoading ? <Skeleton className="h-64" /> : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={byDistrict.data?.slice(0, 10)}>
                <XAxis dataKey="district" tick={{ fontSize: 9 }} interval={0} angle={-35} textAnchor="end" height={70} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#0EA5E9" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="mb-3 font-sora font-semibold">University leaderboard</h2>
          <div className="space-y-2">
            {leaderboard.data?.slice(0, 8).map((u, i) => (
              <div key={u.university_id} className="flex items-center justify-between rounded-lg bg-black/5 px-3 py-2 text-sm dark:bg-white/5">
                <span>{i + 1}. {u.name}</span>
                <span className="text-xs text-muted">{u.projects_count} projects · avg {u.avg_score}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h2 className="mb-3 font-sora font-semibold">Outcomes</h2>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Patents filed", value: outcomes.data?.patents_filed },
              { label: "Startups spawned", value: outcomes.data?.startups_spawned },
              { label: "Pilots deployed", value: outcomes.data?.pilots_deployed },
              { label: "Beneficiaries impacted", value: outcomes.data?.total_beneficiaries_impacted },
            ].map((o) => (
              <div key={o.label} className="rounded-xl bg-primary-soft p-4 text-center">
                <p className="font-mono text-xl font-bold text-primary">{o.value ?? "—"}</p>
                <p className="mt-1 text-xs text-muted">{o.label}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </motion.div>
  );
}
