"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useDropzone } from "react-dropzone";
import { UploadCloud, MapPin } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import type { ChallengeOut } from "@/types";
import { Button } from "@/components/ui/Button";
import { Card, Input, Textarea } from "@/components/ui/primitives";
import { AITriagePanel } from "@/components/AITriagePanel";
import { pageTransition } from "@/lib/motion";

export default function NewChallengePage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [district, setDistrict] = useState(user?.district ?? "");
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [beneficiaries, setBeneficiaries] = useState(0);
  const [files, setFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "image/*": [], "application/pdf": [] },
    onDrop: (accepted) => setFiles((prev) => [...prev, ...accepted]),
  });

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation isn't supported by your browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude);
        setLng(pos.coords.longitude);
        toast.success("Location captured");
      },
      () => toast.error("Couldn't get your location")
    );
  };

  const onSubmit = async () => {
    if (!user) {
      toast.error("Please log in to report a challenge");
      router.push("/login");
      return;
    }
    if (title.trim().length < 5 || description.trim().length < 20 || !district.trim()) {
      toast.error("Please fill in the title, description (20+ chars), and district");
      return;
    }

    setIsSubmitting(true);
    try {
      const form = new FormData();
      form.append("title", title);
      form.append("description", description);
      form.append("district", district);
      if (lat !== null) form.append("lat", String(lat));
      if (lng !== null) form.append("lng", String(lng));
      form.append("beneficiaries_estimate", String(beneficiaries));
      files.forEach((f) => form.append("files", f));

      const { data } = await api.post<ChallengeOut>("/challenges", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Challenge submitted — AI triage complete");
      router.push(`/challenges/${data.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Submission failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div {...pageTransition} className="mx-auto max-w-2xl space-y-6">
      <h1 className="font-sora text-2xl font-bold">Report a challenge</h1>

      <Card className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Title</label>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Brief, specific title" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Description</label>
          <Textarea rows={5} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What's happening, where, and who is affected?" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium">District</label>
            <Input value={district} onChange={(e) => setDistrict(e.target.value)} placeholder="e.g. Ranchi" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Estimated beneficiaries</label>
            <Input type="number" min={0} value={beneficiaries} onChange={(e) => setBeneficiaries(Number(e.target.value))} />
          </div>
        </div>

        <button type="button" onClick={useMyLocation} className="flex items-center gap-1.5 text-sm text-primary">
          <MapPin className="h-4 w-4" /> {lat && lng ? `Location captured (${lat.toFixed(3)}, ${lng.toFixed(3)})` : "Use my current location"}
        </button>

        <div {...getRootProps()} className={`cursor-pointer rounded-xl border-2 border-dashed p-6 text-center text-sm ${isDragActive ? "border-primary bg-primary-soft" : "border-border-light dark:border-border-dark"}`}>
          <input {...getInputProps()} />
          <UploadCloud className="mx-auto mb-2 h-6 w-6 text-muted" />
          {files.length > 0 ? `${files.length} file(s) attached` : "Drag & drop photos or a PDF, or click to select"}
        </div>
      </Card>

      <AITriagePanel title={title} description={description} district={district} />

      <Button onClick={onSubmit} isLoading={isSubmitting} className="w-full" size="lg">
        Submit challenge
      </Button>
    </motion.div>
  );
}
