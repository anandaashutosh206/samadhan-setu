"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, MapPin, ArrowBigUp } from "lucide-react";
import type { ChallengeOut } from "@/types";
import { DomainBadge, SeverityBadge } from "@/components/ui/primitives";
import { springSoft } from "@/lib/motion";

const domainColors: Record<string, string> = {
  agriculture: "#16A34A", healthcare: "#DC2626", water_resources: "#0EA5E9", education: "#4F46E5",
  energy: "#F59E0B", environment: "#14B8A6", urban_development: "#8B5CF6", accessibility: "#EC4899",
  public_administration: "#64748B", rural_livelihoods: "#D97706",
};

const severityStroke: Record<string, number> = { low: 0.25, medium: 0.5, high: 0.75, critical: 1 };

export function ChallengeCard({ challenge }: { challenge: ChallengeOut }) {
  const [open, setOpen] = useState(false);
  const color = domainColors[challenge.domain] ?? "#64748B";
  const dash = severityStroke[challenge.severity] ?? 0.5;

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01, boxShadow: `0 12px 30px -8px ${color}55` }}
      transition={{ type: "spring", stiffness: 400, damping: 28 }}
      className="glass-card relative overflow-hidden p-5"
      style={{ borderColor: `${color}33` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <DomainBadge domain={challenge.domain} />
            <SeverityBadge severity={challenge.severity} />
          </div>
          <Link href={`/challenges/${challenge.id}`} className="block truncate font-sora font-semibold hover:text-primary">
            {challenge.title}
          </Link>
          <p className="mt-1 line-clamp-2 text-sm text-muted">{challenge.ai_summary ?? challenge.description}</p>
          <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted">
            <span className="inline-flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{challenge.district}</span>
            <span className="inline-flex items-center gap-1"><ArrowBigUp className="h-3.5 w-3.5" />{challenge.upvote_count} upvotes</span>
            <span>{challenge.status.replace(/_/g, " ")}</span>
          </div>
        </div>

        <div className="flex flex-col items-center gap-1">
          <svg width="52" height="52" viewBox="0 0 52 52">
            <circle cx="26" cy="26" r="22" fill="none" stroke="currentColor" strokeOpacity="0.1" strokeWidth="5" />
            <motion.circle
              cx="26" cy="26" r="22" fill="none" stroke={color} strokeWidth="5" strokeLinecap="round"
              strokeDasharray={2 * Math.PI * 22}
              initial={{ strokeDashoffset: 2 * Math.PI * 22 }}
              animate={{ strokeDashoffset: 2 * Math.PI * 22 * (1 - dash) }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              transform="rotate(-90 26 26)"
            />
          </svg>
          <span className="font-mono text-xs font-semibold" style={{ color }}>{Math.round(challenge.priority_score)}</span>
        </div>
      </div>

      <button
        onClick={() => setOpen((v) => !v)}
        className="mt-3 flex items-center gap-1 text-xs font-medium text-primary"
      >
        Why this priority?
        <motion.span animate={{ rotate: open ? 180 : 0 }}><ChevronDown className="h-3.5 w-3.5" /></motion.span>
      </button>

      <AnimatePresence initial={false}>
        {open ? (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={springSoft}
            className="overflow-hidden"
          >
            <div className="mt-3 space-y-1.5 border-t border-border-light pt-3 text-xs dark:border-border-dark">
              <FactorBar label="AI confidence" value={(challenge.ai_confidence ?? 0) * 100} color={color} />
              <FactorBar label="Beneficiaries reached" value={Math.min(100, (challenge.beneficiaries_estimate / 5000) * 100)} color={color} />
              <FactorBar label="Community upvotes" value={Math.min(100, (challenge.upvote_count / 100) * 100)} color={color} />
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </motion.div>
  );
}

function FactorBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="mb-0.5 flex justify-between text-muted"><span>{label}</span><span>{Math.round(value)}%</span></div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-black/5 dark:bg-white/10">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}
