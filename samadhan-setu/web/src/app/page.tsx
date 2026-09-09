"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowRight, GraduationCap, Building2, Landmark, Users } from "lucide-react";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import type { AnalyticsOverview } from "@/types";
import { Card } from "@/components/ui/primitives";
import { scrollReveal, listContainer, listItem } from "@/lib/motion";

const stakeholders = [
  { role: "Citizens & Community Orgs", desc: "Report a local problem with a photo, location, and details in minutes.", icon: Users, href: "/challenges/new" },
  { role: "Universities", desc: "Discover challenges matched to your faculty's research strengths.", icon: GraduationCap, href: "/universities" },
  { role: "Industry & Startups", desc: "Fund, mentor, or pilot student-built solutions ready for deployment.", icon: Building2, href: "/industries" },
  { role: "Government Officials", desc: "Validate, prioritise, and track outcomes district by district.", icon: Landmark, href: "/analytics" },
];

export default function LandingPage() {
  const { data } = useQuery({
    queryKey: queryKeys.analyticsOverview,
    queryFn: async () => (await api.get<AnalyticsOverview>("/analytics/overview")).data,
  });

  return (
    <div className="space-y-20">
      <section className="grid gap-10 pt-8 md:grid-cols-2 md:items-center">
        <div>
          <p className="mb-3 text-sm font-medium text-secondary">Govt. of Jharkhand · Dept. of Higher &amp; Technical Education</p>
          <h1 className="font-sora text-3xl font-bold leading-tight sm:text-4xl">
            Turn a citizen&apos;s complaint into a university-built, industry-funded solution.
          </h1>
          <p className="mt-4 max-w-xl text-muted">
            Samadhan Setu routes real problems from Jharkhand&apos;s villages and towns to the researchers,
            students, and partners equipped to solve them — with AI doing the triage, not the paperwork.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/challenges/new" className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-medium text-white hover:bg-primary-hover">
              Report a challenge <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/challenges" className="inline-flex items-center gap-2 rounded-xl border border-border-light px-5 py-3 text-sm font-medium dark:border-border-dark">
              Browse challenges
            </Link>
          </div>
        </div>

        <motion.div {...scrollReveal} className="grid grid-cols-2 gap-4">
          {[
            { label: "Challenges submitted", value: data?.total_challenges },
            { label: "Universities onboard", value: data?.total_universities },
            { label: "Active proposals", value: data?.total_proposals },
            { label: "Citizens reached", value: data?.total_beneficiaries },
          ].map((stat) => (
            <Card key={stat.label} className="text-center">
              <p className="font-mono text-2xl font-bold text-primary">{stat.value ?? "—"}</p>
              <p className="mt-1 text-xs text-muted">{stat.label}</p>
            </Card>
          ))}
        </motion.div>
      </section>

      <motion.section variants={listContainer} initial="initial" whileInView="animate" viewport={{ once: true, margin: "-80px" }}>
        <h2 className="mb-6 font-sora text-xl font-semibold">Built for every stakeholder in the loop</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stakeholders.map(({ role, desc, icon: Icon, href }) => (
            <motion.div key={role} variants={listItem}>
              <Link href={href}>
                <Card hoverable className="h-full">
                  <Icon className="mb-3 h-6 w-6 text-primary" />
                  <p className="font-sora font-semibold">{role}</p>
                  <p className="mt-1 text-sm text-muted">{desc}</p>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      </motion.section>

      <section className="grid gap-4 sm:grid-cols-3">
        {[
          { step: "1. Citizen reports", desc: "A photo, location, and description — AI classifies domain, severity, and checks for duplicates instantly." },
          { step: "2. Govt validates & AI routes", desc: "Officials confirm priority; the match engine ranks universities by discipline fit, research focus, and load." },
          { step: "3. University + industry deliver", desc: "Student teams propose, industry partners fund or pilot, and progress tracks through to deployment." },
        ].map((s) => (
          <Card key={s.step}>
            <p className="font-sora font-semibold text-primary">{s.step}</p>
            <p className="mt-2 text-sm text-muted">{s.desc}</p>
          </Card>
        ))}
      </section>
    </div>
  );
}
