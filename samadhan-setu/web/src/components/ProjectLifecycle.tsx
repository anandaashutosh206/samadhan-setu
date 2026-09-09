"use client";

import { useState } from "react";
import { motion, AnimatePresence, Reorder } from "framer-motion";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { MilestoneOut } from "@/types";
import { Progress } from "@/components/ui/primitives";

const STAGES = ["ACTIVE", "IN_REVIEW", "PILOT", "DEPLOYED", "COMPLETED"];

export function LifecycleStepper({ status, progress }: { status: string; progress: number }) {
  const activeIndex = Math.max(0, STAGES.findIndex((s) => s === status.toUpperCase()));
  return (
    <div className="space-y-3">
      <div className="relative flex items-center justify-between overflow-x-auto pb-2">
        <div className="absolute left-0 top-1/2 h-0.5 w-full -translate-y-1/2 bg-black/10 dark:bg-white/10" />
        <motion.div
          className="absolute left-0 top-1/2 h-0.5 -translate-y-1/2 bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${(activeIndex / (STAGES.length - 1)) * 100}%` }}
          transition={{ type: "spring", stiffness: 120, damping: 20 }}
        />
        {STAGES.map((stage, i) => (
          <div key={stage} className="relative z-10 flex flex-col items-center gap-1 px-2">
            <motion.div
              className="h-3 w-3 rounded-full"
              animate={{ backgroundColor: i <= activeIndex ? "var(--primary)" : "rgba(100,116,139,0.3)", scale: i === activeIndex ? 1.4 : 1 }}
            />
            <span className="whitespace-nowrap text-[10px] text-muted">{stage.replace(/_/g, " ")}</span>
          </div>
        ))}
      </div>
      <Progress value={progress} />
      <p className="text-right text-xs text-muted">{progress}% complete</p>
    </div>
  );
}

const COLUMNS: { key: string; label: string }[] = [
  { key: "PENDING", label: "Pending" },
  { key: "IN_REVIEW", label: "In Review" },
  { key: "APPROVED", label: "Approved" },
  { key: "BLOCKED", label: "Blocked" },
];

export function MilestoneKanban({ milestones, onStatusChange }: { milestones: MilestoneOut[]; onStatusChange: (id: string, status: string) => Promise<void> }) {
  const [items, setItems] = useState(milestones);
  const [dragging, setDragging] = useState<string | null>(null);

  const moveTo = async (id: string, newStatus: string) => {
    const prev = items;
    setItems((cur) => cur.map((m) => (m.id === id ? { ...m, status: newStatus } : m)));
    try {
      await onStatusChange(id, newStatus);
    } catch {
      setItems(prev);
      toast.error("Couldn't update milestone — reverted");
    }
  };

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {COLUMNS.map((col) => (
        <div
          key={col.key}
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => dragging && moveTo(dragging, col.key)}
          className="min-h-[120px] rounded-xl bg-black/5 p-2 dark:bg-white/5"
        >
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">{col.label}</p>
          <AnimatePresence>
            {items.filter((m) => m.status === col.key).map((m) => (
              <motion.div
                key={m.id}
                layoutId={m.id}
                draggable
                onDragStart={() => setDragging(m.id)}
                onDragEnd={() => setDragging(null)}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="mb-2 cursor-grab rounded-lg bg-surface-light p-2.5 text-xs shadow-sm active:cursor-grabbing dark:bg-surface-dark"
              >
                <p className="font-medium">{m.title}</p>
                {m.due_date ? <p className="mt-1 text-muted">Due {new Date(m.due_date).toLocaleDateString()}</p> : null}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
}
