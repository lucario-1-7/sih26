'use client';

import { useEffect } from 'react';
import { useAppStore } from '@/store/useAppStore';

/** Runs once on app load: if a token is already stored, confirms it's still
 * valid against the real backend (GET /users/me) before treating the
 * citizen as logged in — never assumes a stored token is still good. */
export function SessionHydrator() {
  const hydrateSession = useAppStore((s) => s.hydrateSession);

  useEffect(() => {
    void hydrateSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
}
