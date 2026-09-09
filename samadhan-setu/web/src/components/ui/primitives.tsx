"use client";

import { forwardRef, type HTMLAttributes, type InputHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { hoverLift } from "@/lib/motion";

export function Card({ className, hoverable, ...props }: HTMLAttributes<HTMLDivElement> & { hoverable?: boolean }) {
  const Comp = hoverable ? motion.div : "div";
  const motionProps = hoverable ? hoverLift : {};
  return <Comp className={cn("glass-card shadow-glass p-5", className)} {...motionProps} {...(props as any)} />;
}

const domainColors: Record<string, string> = {
  agriculture: "#16A34A", healthcare: "#DC2626", water_resources: "#0EA5E9", education: "#4F46E5",
  energy: "#F59E0B", environment: "#14B8A6", urban_development: "#8B5CF6", accessibility: "#EC4899",
  public_administration: "#64748B", rural_livelihoods: "#D97706",
};

export function DomainBadge({ domain }: { domain: string }) {
  const color = domainColors[domain] ?? "#64748B";
  return (
    <span
      className="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium"
      style={{ backgroundColor: `${color}1A`, color }}
    >
      {domain.replace(/_/g, " ")}
    </span>
  );
}

const severityColors: Record<string, string> = {
  low: "#16A34A", medium: "#F59E0B", high: "#DC2626", critical: "#7F1D1D",
};

export function SeverityBadge({ severity }: { severity: string }) {
  const color = severityColors[severity] ?? "#64748B";
  return (
    <span className="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium" style={{ backgroundColor: `${color}1A`, color }}>
      {severity}
    </span>
  );
}

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full bg-primary-soft px-2.5 py-1 text-xs font-medium text-primary",
        className
      )}
      {...props}
    />
  );
}

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "w-full rounded-xl border border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark px-3.5 py-2.5 text-sm outline-none transition-shadow focus:ring-2 focus:ring-primary/40",
      className
    )}
    {...props}
  />
));
Input.displayName = "Input";

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "w-full rounded-xl border border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark px-3.5 py-2.5 text-sm outline-none transition-shadow focus:ring-2 focus:ring-primary/40",
      className
    )}
    {...props}
  />
));
Textarea.displayName = "Textarea";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(({ className, children, ...props }, ref) => (
  <select
    ref={ref}
    className={cn(
      "w-full rounded-xl border border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark px-3.5 py-2.5 text-sm outline-none transition-shadow focus:ring-2 focus:ring-primary/40",
      className
    )}
    {...props}
  >
    {children}
  </select>
));
Select.displayName = "Select";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-lg bg-black/5 dark:bg-white/10", className)} />;
}

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="glass-card flex flex-col items-center gap-1 py-14 text-center">
      <p className="font-sora text-lg font-semibold">{title}</p>
      {description ? <p className="max-w-md text-sm text-muted">{description}</p> : null}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="glass-card border-danger/30 py-10 text-center text-sm text-danger">
      {message}
    </div>
  );
}

export function Progress({ value }: { value: number }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-black/5 dark:bg-white/10">
      <motion.div
        className="h-full rounded-full bg-primary"
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        transition={{ type: "spring", stiffness: 120, damping: 20 }}
      />
    </div>
  );
}
