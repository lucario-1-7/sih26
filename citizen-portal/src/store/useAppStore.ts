import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { Problem, User, Language, TextScale } from '@/types';
import { challengesApi, mapBackendChallengeToProblem, CreateChallengeInput } from '@/lib/api/challengesApi';
import { authApi } from '@/lib/api/authApi';
import { administrativeAreaApi, AdministrativeArea } from '@/lib/api/administrativeAreaApi';
import { ApiError } from '@/lib/api/client';

interface ToastState {
  show: boolean;
  title: string;
  message: string;
  type: 'success' | 'info' | 'error';
}

interface AppStore {
  // Localization & Display Settings
  language: Language;
  setLanguage: (lang: Language) => void;
  textScale: TextScale;
  setTextScale: (scale: TextScale) => void;
  cycleTextScale: () => void;
  decreaseTextScale: () => void;
  increaseTextScale: () => void;

  // Authenticated Citizen State — real backend session only. `user` is
  // null until a real MSG91-verified login completes; there is no demo
  // default account.
  user: User | null;
  isHydrating: boolean;
  hydrateSession: () => Promise<void>;
  /** Called after a real MSG91 access-token has already been verified by
   * the backend (authApi.verifyMsg91AccessToken succeeded). Fetches the
   * real authenticated profile — never fabricates one. */
  completeLogin: () => Promise<void>;
  logoutUser: () => Promise<void>;

  // Administrative areas — the backend is authoritative; no static list.
  administrativeAreas: AdministrativeArea[];
  loadAdministrativeAreas: () => Promise<void>;

  // Problem Repository State — sourced only from the real backend.
  problems: Problem[];
  isLoadingProblems: boolean;
  problemsError: string | null;
  syncLiveChallenges: () => Promise<void>;
  getProblemById: (idOrTrackingCode: string) => Problem | undefined;
  fetchProblemById: (id: string) => Promise<Problem | null>;
  addProblem: (input: {
    title: string;
    description: string;
    administrative_area_id: string;
    pin_code?: string;
  }) => Promise<Problem>;

  // Upvotes: the backend has no upvote/support concept for a challenge at
  // all (no endpoint, no column) — this is intentionally local-only,
  // per-browser-session state, never presented as synced across devices.
  userUpvotes: Record<string, boolean>;
  hasUserUpvoted: (problemId: string) => boolean;
  upvoteProblem: (problemId: string) => { success: boolean; message?: string };

  // Global Toast
  toast: ToastState | null;
  showToast: (title: string, message: string, type?: 'success' | 'info' | 'error') => void;
  hideToast: () => void;
}

function mapUser(backendUser: { id: string; phone: string; name: string }): User {
  return {
    id: backendUser.id,
    fullName: backendUser.name,
    phone: backendUser.phone,
    isVerified: true,
  };
}

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Defaults
      language: 'en',
      setLanguage: (lang) => set({ language: lang }),

      textScale: 'normal',
      setTextScale: (scale) => set({ textScale: scale }),
      cycleTextScale: () => {
        const current = get().textScale;
        const next: TextScale = current === 'normal' ? 'large' : current === 'large' ? 'larger' : 'normal';
        set({ textScale: next });
      },
      decreaseTextScale: () => {
        const current = get().textScale;
        if (current === 'larger') set({ textScale: 'large' });
        else if (current === 'large') set({ textScale: 'normal' });
      },
      increaseTextScale: () => {
        const current = get().textScale;
        if (current === 'normal') set({ textScale: 'large' });
        else if (current === 'large') set({ textScale: 'larger' });
      },

      user: null,
      isHydrating: true,

      hydrateSession: async () => {
        if (!authApi.hasSession()) {
          set({ isHydrating: false });
          return;
        }
        try {
          const backendUser = await authApi.getCurrentUser();
          set({ user: mapUser(backendUser), isHydrating: false });
        } catch {
          // Stored token is invalid/expired — do not pretend a session exists.
          set({ user: null, isHydrating: false });
        }
      },

      completeLogin: async () => {
        const backendUser = await authApi.getCurrentUser();
        set({ user: mapUser(backendUser) });
      },

      logoutUser: async () => {
        try {
          await authApi.logout();
        } finally {
          set({ user: null, problems: [] });
        }
      },

      administrativeAreas: [],
      loadAdministrativeAreas: async () => {
        try {
          const areas = await administrativeAreaApi.list();
          set({ administrativeAreas: areas });
        } catch {
          set({ administrativeAreas: [] });
        }
      },

      problems: [],
      isLoadingProblems: false,
      problemsError: null,

      syncLiveChallenges: async () => {
        const user = get().user;
        if (!user) {
          set({ problems: [] });
          return;
        }
        set({ isLoadingProblems: true, problemsError: null });
        try {
          const items = await challengesApi.getMyChallenges(user.id);
          const areas = get().administrativeAreas.length
            ? get().administrativeAreas
            : await administrativeAreaApi.list().catch(() => []);
          const areaNameById = new Map(areas.map((a) => [a.id, a.name]));
          const problems = items.map((c) =>
            mapBackendChallengeToProblem(c, {
              areaName: areaNameById.get(c.administrative_area_id),
              currentUserId: user.id,
              currentUserName: user.fullName,
              currentUserPhone: user.phone,
            })
          );
          set({ problems, isLoadingProblems: false });
        } catch (err) {
          const message = err instanceof ApiError ? err.message : 'Could not load your reports.';
          set({ isLoadingProblems: false, problemsError: message });
        }
      },

      getProblemById: (idOrTrackingCode: string) => {
        return get().problems.find(
          (p) =>
            p.id.toLowerCase() === idOrTrackingCode.toLowerCase() ||
            p.trackingCode.toLowerCase() === idOrTrackingCode.toLowerCase()
        );
      },

      fetchProblemById: async (id: string) => {
        const cached = get().getProblemById(id);
        if (cached) return cached;
        try {
          const c = await challengesApi.getChallengeById(id);
          const areas = get().administrativeAreas.length
            ? get().administrativeAreas
            : await administrativeAreaApi.list().catch(() => []);
          const areaName = areas.find((a) => a.id === c.administrative_area_id)?.name;
          const user = get().user;
          return mapBackendChallengeToProblem(c, {
            areaName,
            currentUserId: user?.id,
            currentUserName: user?.fullName,
            currentUserPhone: user?.phone,
          });
        } catch {
          return null;
        }
      },

      addProblem: async (input) => {
        const created = await challengesApi.createChallenge(input as CreateChallengeInput);
        const user = get().user;
        const areaName = get().administrativeAreas.find((a) => a.id === created.administrative_area_id)?.name;
        const problem = mapBackendChallengeToProblem(created, {
          areaName,
          currentUserId: user?.id,
          currentUserName: user?.fullName,
          currentUserPhone: user?.phone,
        });
        set({ problems: [problem, ...get().problems] });
        return problem;
      },

      userUpvotes: {},
      hasUserUpvoted: (problemId: string) => Boolean(get().userUpvotes[problemId]),
      upvoteProblem: (problemId: string) => {
        if (get().userUpvotes[problemId]) {
          return { success: false, message: 'You have already upvoted this problem.' };
        }
        set({
          userUpvotes: { ...get().userUpvotes, [problemId]: true },
          problems: get().problems.map((p) => (p.id === problemId ? { ...p, upvotes: p.upvotes + 1 } : p)),
        });
        return { success: true };
      },

      toast: null,
      showToast: (title, message, type = 'success') => {
        set({ toast: { show: true, title, message, type } });
      },
      hideToast: () => set({ toast: null }),
    }),
    {
      name: 'sociosolve-citizen-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        language: state.language,
        textScale: state.textScale,
      }),
    }
  )
);
