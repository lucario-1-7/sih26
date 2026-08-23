"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth/AuthContext";
import { Spinner } from "@/components/ui/Spinner";

/**
 * Generic entry point. Kept intentionally minimal/additive — the Citizen
 * Dashboard owns its own `/citizen` route tree; this file only routes
 * unauthenticated visitors to `/login` and authenticated organizational
 * users to their dashboard. It does not assume ownership of `/`.
 */
export default function HomePage() {
  const { user, status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "loading") return;
    if (status === "unauthenticated" || !user) {
      router.replace("/login");
      return;
    }
    if (user.domain === "citizen") {
      router.replace("/citizen");
      return;
    }
    router.replace("/organization");
  }, [status, user, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Spinner label="Loading SocioSolve…" />
    </div>
  );
}
