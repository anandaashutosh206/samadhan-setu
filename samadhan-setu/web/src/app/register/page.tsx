"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { Card, Input, Select } from "@/components/ui/primitives";
import { pageTransition } from "@/lib/motion";
import type { TokenPair, Role } from "@/types";

const schema = z.object({
  name: z.string().min(2, "Name is too short"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "At least 8 characters"),
  role: z.enum([
    "CITIZEN", "COMMUNITY_ORG", "UNIVERSITY_ADMIN", "FACULTY_MENTOR",
    "STUDENT", "INDUSTRY_PARTNER", "GOVT_OFFICIAL",
  ]),
  district: z.string().optional(),
  org_name: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

const roleOptions: { value: Role; label: string }[] = [
  { value: "CITIZEN", label: "Citizen" },
  { value: "COMMUNITY_ORG", label: "Community Org (PRI / ULB)" },
  { value: "UNIVERSITY_ADMIN", label: "University Admin" },
  { value: "FACULTY_MENTOR", label: "Faculty Mentor" },
  { value: "STUDENT", label: "Student" },
  { value: "INDUSTRY_PARTNER", label: "Industry / Startup / CSR Partner" },
  { value: "GOVT_OFFICIAL", label: "Government Official" },
];

export default function RegisterPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: "CITIZEN" },
  });

  const onSubmit = async (values: FormValues) => {
    setIsSubmitting(true);
    try {
      const { data } = await api.post<TokenPair>("/auth/register", values);
      login(data.access_token, data.refresh_token, data.user);
      toast.success("Account created");
      router.push("/challenges");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div {...pageTransition} className="mx-auto max-w-md">
      <Card>
        <h1 className="font-sora text-xl font-semibold">Create your account</h1>
        <p className="mt-1 text-sm text-muted">Choose the role that matches how you&apos;ll use Samadhan Setu.</p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Full name</label>
            <Input placeholder="Your name" {...register("name")} />
            {errors.name ? <p className="mt-1 text-xs text-danger">{errors.name.message}</p> : null}
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <Input type="email" placeholder="you@example.com" {...register("email")} />
            {errors.email ? <p className="mt-1 text-xs text-danger">{errors.email.message}</p> : null}
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <Input type="password" placeholder="At least 8 characters" {...register("password")} />
            {errors.password ? <p className="mt-1 text-xs text-danger">{errors.password.message}</p> : null}
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">I am a...</label>
            <Select {...register("role")}>
              {roleOptions.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </Select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">District (optional)</label>
            <Input placeholder="e.g. Ranchi" {...register("district")} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Organisation (optional)</label>
            <Input placeholder="e.g. BIT Sindri" {...register("org_name")} />
          </div>
          <Button type="submit" className="w-full" isLoading={isSubmitting}>Create account</Button>
        </form>
      </Card>
    </motion.div>
  );
}
