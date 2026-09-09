"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/primitives";
import { Input } from "@/components/ui/primitives";
import { pageTransition } from "@/lib/motion";
import type { TokenPair } from "@/types";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});
type FormValues = z.infer<typeof schema>;

const demoAccounts = [
  { label: "Citizen", email: "citizen@jharkhand.gov.in" },
  { label: "Govt Official", email: "govt@jharkhand.gov.in" },
  { label: "University Admin", email: "university@jharkhand.gov.in" },
  { label: "Industry Partner", email: "industry@jharkhand.gov.in" },
];

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    setIsSubmitting(true);
    try {
      const { data } = await api.post<TokenPair>("/auth/login", values);
      login(data.access_token, data.refresh_token, data.user);
      toast.success(`Welcome back, ${data.user.name}`);
      router.push("/challenges");
    } catch {
      toast.error("Invalid email or password");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div {...pageTransition} className="mx-auto max-w-md">
      <Card>
        <h1 className="font-sora text-xl font-semibold">Log in</h1>
        <p className="mt-1 text-sm text-muted">Access your Samadhan Setu dashboard.</p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <Input type="email" placeholder="you@example.com" {...register("email")} />
            {errors.email ? <p className="mt-1 text-xs text-danger">{errors.email.message}</p> : null}
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <Input type="password" placeholder="••••••••" {...register("password")} />
            {errors.password ? <p className="mt-1 text-xs text-danger">{errors.password.message}</p> : null}
          </div>
          <Button type="submit" className="w-full" isLoading={isSubmitting}>Log in</Button>
        </form>

        <p className="mt-4 text-center text-sm text-muted">
          No account? <Link href="/register" className="text-primary">Sign up</Link>
        </p>

        <div className="mt-6 border-t border-border-light pt-4 dark:border-border-dark">
          <p className="mb-2 text-xs uppercase tracking-wide text-muted">Judge demo mode — password Demo@1234</p>
          <div className="flex flex-wrap gap-2">
            {demoAccounts.map((d) => (
              <button
                key={d.email}
                type="button"
                onClick={() => {
                  setValue("email", d.email);
                  setValue("password", "Demo@1234");
                }}
                className="rounded-full border border-border-light px-3 py-1 text-xs hover:bg-black/5 dark:border-border-dark dark:hover:bg-white/10"
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
