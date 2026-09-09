"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { ArrowBigUp, Download, MapPin, Send } from "lucide-react";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import { useAuthStore } from "@/store/auth";
import type { AIDuplicateCandidate, AIMatchResponse, ChallengeOut, CommentOut } from "@/types";
import { Button } from "@/components/ui/Button";
import { Card, DomainBadge, SeverityBadge, Skeleton, Textarea, ErrorState } from "@/components/ui/primitives";
import { pageTransition } from "@/lib/motion";

export default function ChallengeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const user = useAuthStore((s) => s.user);
  const qc = useQueryClient();
  const [commentBody, setCommentBody] = useState("");

  const { data: challenge, isLoading, isError } = useQuery({
    queryKey: queryKeys.challenge(id),
    queryFn: async () => (await api.get<ChallengeOut>(`/challenges/${id}`)).data,
  });

  const { data: similar } = useQuery({
    queryKey: queryKeys.challengeSimilar(id),
    queryFn: async () => (await api.get<AIDuplicateCandidate[]>(`/challenges/${id}/similar`)).data,
    enabled: !!challenge,
  });

  const { data: routing } = useQuery({
    queryKey: queryKeys.challengeRouting(id),
    queryFn: async () => (await api.get<AIMatchResponse>(`/challenges/${id}/routing-suggestions`)).data,
    enabled: !!challenge,
  });

  const { data: comments } = useQuery({
    queryKey: queryKeys.comments("challenge", id),
    queryFn: async () => (await api.get<CommentOut[]>("/comments", { params: { entity_type: "challenge", entity_id: id } })).data,
    enabled: !!challenge,
  });

  const upvoteMutation = useMutation({
    mutationFn: async () => (await api.post<ChallengeOut>(`/challenges/${id}/upvote`)).data,
    onSuccess: (data) => qc.setQueryData(queryKeys.challenge(id), data),
    onError: () => toast.error("Please log in to upvote"),
  });

  const commentMutation = useMutation({
    mutationFn: async () => (await api.post<CommentOut>("/comments", { entity_type: "challenge", entity_id: id, body: commentBody })).data,
    onSuccess: () => {
      setCommentBody("");
      qc.invalidateQueries({ queryKey: queryKeys.comments("challenge", id) });
    },
    onError: () => toast.error("Please log in to comment"),
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-40" />
      </div>
    );
  }
  if (isError || !challenge) return <ErrorState message="Challenge not found." />;

  return (
    <motion.div {...pageTransition} className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-6 lg:col-span-2">
        <Card>
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <DomainBadge domain={challenge.domain} />
            <SeverityBadge severity={challenge.severity} />
            <span className="text-xs text-muted">{challenge.status.replace(/_/g, " ")}</span>
          </div>
          <h1 className="font-sora text-2xl font-bold">{challenge.title}</h1>
          <p className="mt-1 flex items-center gap-1 text-sm text-muted"><MapPin className="h-3.5 w-3.5" />{challenge.district}</p>
          <p className="mt-4 whitespace-pre-line text-sm">{challenge.description}</p>

          {challenge.ai_summary ? (
            <div className="mt-4 rounded-xl bg-primary-soft p-3 text-sm">
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-primary">AI summary</p>
              {challenge.ai_summary}
            </div>
          ) : null}

          {challenge.ai_keywords.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {challenge.ai_keywords.map((k) => <span key={k} className="rounded-full bg-black/5 px-2 py-0.5 text-xs dark:bg-white/10">{k}</span>)}
            </div>
          ) : null}

          <div className="mt-5 flex flex-wrap gap-3">
            <Button variant="ghost" size="sm" onClick={() => upvoteMutation.mutate()}>
              <ArrowBigUp className="h-4 w-4" /> {challenge.upvote_count} Upvote
            </Button>
            <a href={`${process.env.NEXT_PUBLIC_API_URL}/reports/challenge/${challenge.id}.pdf`} target="_blank" rel="noreferrer">
              <Button variant="ghost" size="sm"><Download className="h-4 w-4" /> Export PDF</Button>
            </a>
          </div>
        </Card>

        <Card>
          <h2 className="mb-3 font-sora font-semibold">Discussion</h2>
          <div className="space-y-3">
            {comments && comments.length > 0 ? (
              comments.map((c) => (
                <div key={c.id} className="rounded-xl bg-black/5 p-3 text-sm dark:bg-white/5">
                  {c.body}
                  <p className="mt-1 text-xs text-muted">{new Date(c.created_at).toLocaleString()}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted">No comments yet. Be the first to add context.</p>
            )}
          </div>

          {user ? (
            <div className="mt-4 flex gap-2">
              <Textarea rows={2} value={commentBody} onChange={(e) => setCommentBody(e.target.value)} placeholder="Add a comment..." />
              <Button onClick={() => commentMutation.mutate()} disabled={!commentBody.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          ) : null}
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <h2 className="mb-3 font-sora font-semibold">Suggested universities</h2>
          {routing && routing.matches.length > 0 ? (
            <div className="space-y-3">
              {routing.matches.map((m) => (
                <div key={m.university_id} className="rounded-xl border border-border-light p-3 text-sm dark:border-border-dark">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{m.name}</span>
                    <span className="font-mono text-xs text-primary">{m.match_score}%</span>
                  </div>
                  <p className="text-xs text-muted">{m.district}</p>
                  <ul className="mt-1 list-disc pl-4 text-xs text-muted">
                    {m.match_reasons.slice(0, 3).map((r) => <li key={r}>{r}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">No matches yet.</p>
          )}
        </Card>

        <Card>
          <h2 className="mb-3 font-sora font-semibold">Similar reports</h2>
          {similar && similar.length > 0 ? (
            <div className="space-y-2">
              {similar.map((s) => (
                <div key={s.challenge_id} className="rounded-xl bg-black/5 p-3 text-xs dark:bg-white/5">
                  <p className="font-medium">{s.title}</p>
                  <p className="text-muted">{Math.round(s.similarity * 100)}% similar — {s.reasons[0]}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">No similar reports found.</p>
          )}
        </Card>
      </div>
    </motion.div>
  );
}
