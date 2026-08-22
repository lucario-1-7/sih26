"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { requestOtp } from "@/lib/api/auth";
import { authErrorMessage } from "@/components/ui/ErrorState";
import { useAuth } from "@/lib/auth/AuthContext";
import { Button } from "@/components/ui/Button";
import { Field, Input } from "@/components/ui/Input";

type Step = "phone" | "code";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState<Step>("phone");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleRequestOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await requestOtp(phone);
      setStep("code");
    } catch (err) {
      setError(authErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const user = await login(phone, code);
      if (user.domain === "citizen") {
        router.replace("/citizen");
      } else {
        router.replace("/organization");
      }
    } catch (err) {
      setError(authErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="mb-1 text-lg font-semibold text-slate-900">Sign in to Sahyog</h1>
        <p className="mb-6 text-sm text-slate-500">
          {step === "phone" ? "Enter your registered phone number." : "Enter the OTP sent to your phone."}
        </p>

        {step === "phone" ? (
          <form onSubmit={handleRequestOtp} className="flex flex-col gap-4">
            <Field label="Phone number" htmlFor="phone" error={error ?? undefined}>
              <Input
                id="phone"
                type="tel"
                required
                minLength={8}
                maxLength={20}
                placeholder="+91XXXXXXXXXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                autoComplete="tel"
              />
            </Field>
            <Button type="submit" disabled={submitting}>
              {submitting ? "Sending…" : "Send OTP"}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleVerify} className="flex flex-col gap-4">
            <Field label="One-time code" htmlFor="code" error={error ?? undefined}>
              <Input
                id="code"
                type="text"
                inputMode="numeric"
                required
                minLength={4}
                maxLength={8}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                autoComplete="one-time-code"
              />
            </Field>
            <Button type="submit" disabled={submitting}>
              {submitting ? "Verifying…" : "Verify & sign in"}
            </Button>
            <Button type="button" variant="ghost" onClick={() => setStep("phone")}>
              Use a different number
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
