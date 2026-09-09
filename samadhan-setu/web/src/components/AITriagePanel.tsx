"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, AlertTriangle } from "lucide-react";
import { api } from "@/lib/api";
import type { AIClassifyResponse, AIDuplicateCheckResponse } from "@/types";
import { DomainBadge, SeverityBadge } from "@/components/ui/primitives";

export function AITriagePanel({
  title,
  description,
  district,
  onResult,
}: {
  title: string;
  description: string;
  district: string;
  onResult?: (classify: AIClassifyResponse | null, dup: AIDuplicateCheckResponse | null) => void;
}) {
  const [classify, setClassify] = useState<AIClassifyResponse | null>(null);
  const [dup, setDup] = useState<AIDuplicateCheckResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [confidenceDisplay, setConfidenceDisplay] = useState(0);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (title.trim().length < 5 || description.trim().length < 20) {
      setClassify(null);
      setDup(null);
      onResult?.(null, null);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setIsAnalyzing(true);
      try {
        const [classifyRes, dupRes] = await Promise.all([
          api.post<AIClassifyResponse>("/ai/classify", { title, description }),
          api.post<AIDuplicateCheckResponse>("/ai/duplicate-check", { title, description, district: district || undefined }),
        ]);
        setClassify(classifyRes.data);
        setDup(dupRes.data);
        onResult?.(classifyRes.data, dupRes.data);
      } catch {
        // Silent failure — triage is an assist, never blocks submission
      } finally {
        setIsAnalyzing(false);
      }
    }, 700);

    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [title, description, district]);

  useEffect(() => {
    if (!classify) { setConfidenceDisplay(0); return; }
    const target = Math.round(classify.domain_confidence * 100);
    let current = 0;
    const step = () => {
      current += Math.ceil((target - current) / 4) || (target > current ? 1 : 0);
      setConfidenceDisplay(current);
      if (current < target) requestAnimationFrame(step);
    };
    step();
  }, [classify]);

  if (!isAnalyzing && !classify) return null;

  return (
    <div className="glass-card space-y-4 p-5">
      <div className="flex items-center gap-2 text-sm font-medium text-primary">
        <Sparkles className="h-4 w-4" /> AI Triage
      </div>

      {isAnalyzing ? (
        <div className="relative h-16 overflow-hidden rounded-xl bg-black/5 dark:bg-white/5">
          <motion.div
            className="absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-primary/20 to-transparent"
            animate={{ x: ["-100%", "300%"] }}
            transition={{ duration: 1.1, repeat: Infinity, ease: "linear" }}
          />
        </div>
      ) : classify ? (
        <>
          <div className="flex flex-wrap items-center gap-3">
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
              <DomainBadge domain={classify.domain} />
            </motion.div>
            <SeverityBadge severity={classify.severity} />
            <div className="ml-auto flex items-center gap-2">
              <span className="text-xs text-muted">Confidence</span>
              <span className="font-mono text-sm font-semibold text-primary">{confidenceDisplay}%</span>
            </div>
          </div>

          {classify.keywords.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {classify.keywords.slice(0, 6).map((k) => (
                <span key={k} className="rounded-full bg-black/5 px-2 py-0.5 text-xs dark:bg-white/10">{k}</span>
              ))}
            </div>
          ) : null}

          <AnimatePresence>
            {dup?.is_likely_duplicate ? (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: [0, -6, 6, -3, 3, 0] }}
                transition={{ duration: 0.4 }}
                className="space-y-2 rounded-xl border border-warning/40 bg-warning/10 p-3"
              >
                <p className="flex items-center gap-1.5 text-xs font-medium text-warning">
                  <AlertTriangle className="h-3.5 w-3.5" /> Similar reports already exist
                </p>
                {dup.candidates.slice(0, 2).map((c) => (
                  <p key={c.challenge_id} className="text-xs text-muted">
                    &ldquo;{c.title}&rdquo; — {Math.round(c.similarity * 100)}% similar ({c.reasons[0]})
                  </p>
                ))}
              </motion.div>
            ) : null}
          </AnimatePresence>

          <p className="text-xs italic text-muted">You can override the AI-suggested domain and severity below before submitting.</p>
        </>
      ) : null}
    </div>
  );
}
