"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { requestOtp } from "@/lib/api/auth";
import { authErrorMessage } from "@/components/ui/ErrorState";
import { ApiError } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/AuthContext";
import { Button } from "@/components/ui/Button";
import { Field, Input } from "@/components/ui/Input";

type View = "demo-landing" | "phone" | "code";

// Exactly the org-side personas the backend's demo endpoint supports — see
// server/app/services/auth_service.py DEMO_PERSONAS. No personas invented
// here; "citizen" is deliberately excluded (this is the organization
// portal — citizens use citizen-portal's own demo login).
const DEMO_ROLES: { persona: string; name: string; description: string }[] = [
  {
    persona: "government_validator",
    name: "Government Validator",
    description: "Review and validate government challenges",
  },
  {
    persona: "government_field_assistant",
    name: "Government Field Assistant",
    description: "Manage field-level workflows and assignments",
  },
  {
    persona: "university_coordinator",
    name: "University Coordinator",
    description: "Manage university projects and collaborations",
  },
  {
    persona: "university_faculty",
    name: "Faculty",
    description: "Contribute to university projects and collaborations",
  },
  {
    persona: "industry",
    name: "Industry",
    description: "Access industry participation and opportunities",
  },
  {
    persona: "superadmin",
    name: "Superadmin",
    description: "Access platform administration and controls",
  },
];

// PRESENTATION-ONLY. OFF unless the deployment explicitly sets
// NEXT_PUBLIC_DEMO_MODE=true at build time — this only controls which
// experience is shown; the backend independently re-checks its own
// DEMO_MODE (404s the demo endpoint otherwise), so this flag alone can
// never grant access. Never triggered automatically by a real OTP failure.
const DEMO_MODE_AVAILABLE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

export default function LoginPage() {
  const { login, loginDemo } = useAuth();
  const router = useRouter();
  const [view, setView] = useState<View>(DEMO_MODE_AVAILABLE ? "demo-landing" : "phone");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [demoPersona, setDemoPersona] = useState<string | null>(null);

  async function handleDemoLogin(persona: string) {
    setError(null);
    setDemoPersona(persona);
    try {
      const user = await loginDemo(persona);
      router.replace(user.domain === "citizen" ? "/citizen" : "/organization");
    } catch (err) {
      // A 404 from /auth/demo/login means the backend's own DEMO_MODE is
      // off — that's the only case this specific copy is accurate for.
      // Any other failure (CORS rejection, network error, 5xx) previously
      // showed this same misleading message, masking the real cause.
      if (err instanceof ApiError && err.status === 404) {
        setError("Demo mode is not enabled on this backend.");
      } else {
        setError(authErrorMessage(err));
      }
    } finally {
      setDemoPersona(null);
    }
  }

  async function handleRequestOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await requestOtp(phone);
      setView("code");
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

  if (view === "demo-landing") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
        <div className="w-full max-w-2xl">
          <div className="mb-6 text-center">
            <h1 className="text-2xl font-bold text-slate-900">Sahyog</h1>
            <span className="mt-2 mb-1 inline-block rounded-full bg-amber-400 px-3 py-1 text-xs font-black uppercase tracking-wider text-black">
              Presentation Demo
            </span>
            <p className="mt-2 text-sm text-slate-500">Select a role to continue</p>
          </div>

          {error && (
            <p className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-center text-sm text-red-700">
              {error}
            </p>
          )}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {DEMO_ROLES.map(({ persona, name, description }) => (
              <div key={persona} className="flex flex-col justify-between rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <div>
                  <h2 className="text-sm font-semibold text-slate-900">{name}</h2>
                  <p className="mt-1 text-xs text-slate-500">{description}</p>
                </div>
                <Button
                  type="button"
                  className="mt-4"
                  disabled={demoPersona !== null}
                  onClick={() => void handleDemoLogin(persona)}
                >
                  {demoPersona === persona ? "Signing in…" : `Continue as ${name}`}
                </Button>
              </div>
            ))}
          </div>

          <div className="mt-6 text-center">
            <button
              type="button"
              className="text-xs font-medium text-slate-500 underline hover:text-slate-700"
              onClick={() => setView("phone")}
            >
              Sign in with a real account instead
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="mb-1 text-lg font-semibold text-slate-900">Sign in to Sahyog</h1>
        <p className="mb-6 text-sm text-slate-500">
          {view === "phone" ? "Enter your registered phone number." : "Enter the OTP sent to your phone."}
        </p>

        {view === "phone" ? (
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
            <Button type="button" variant="ghost" onClick={() => setView("phone")}>
              Use a different number
            </Button>
          </form>
        )}

        {DEMO_MODE_AVAILABLE && (
          <div className="mt-6 text-center">
            <button
              type="button"
              className="text-xs font-medium text-slate-500 underline hover:text-slate-700"
              onClick={() => setView("demo-landing")}
            >
              Back to demo role selection
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
