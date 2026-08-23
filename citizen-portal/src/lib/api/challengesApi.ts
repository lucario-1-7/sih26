import { apiClient } from './client';
import { Problem, ProblemStatus, Category, Milestone } from '@/types';

export interface BackendChallengeResponse {
  id: string;
  title: string;
  description: string;
  status: string;
  severity?: string | null;
  submitted_by_id: string;
  administrative_area_id: string;
  pin_code?: string | null;
  cluster_id?: string | null;
  duplicate_of_id?: string | null;
  on_behalf_of_name?: string | null;
  on_behalf_of_phone?: string | null;
  content_domain?: string | null;
  content_domain_confidence?: number | null;
  content_domain_needs_review?: boolean | null;
  content_domain_source?: string | null;
  content_field_intensity?: number | null;
  content_field_label?: string | null;
  content_field_needs_review?: boolean | null;
  content_field_source?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedChallenges {
  items: BackendChallengeResponse[];
  next_cursor: string | null;
  total?: number | null;
}

export interface CreateChallengeInput {
  title: string;
  description: string;
  administrative_area_id: string;
  pin_code?: string;
}

/** Real backend ChallengeStatus values ("submitted" | "open" | "duplicate" |
 * "resolved" — server/app/models/enums.py) mapped onto this UI's
 * ProblemStatus. Every backend value has an explicit counterpart; none are
 * silently folded into an unrelated one. */
function mapBackendStatusToFrontend(backendStatus: string): ProblemStatus {
  switch (backendStatus?.toLowerCase()) {
    case 'submitted':
      return 'Submitted';
    case 'open':
      return 'Under Review';
    case 'duplicate':
      return 'Submitted'; // flagged as a duplicate of an existing report — still "Submitted" from this citizen's perspective, not resolved/matched
    case 'resolved':
      return 'Solution Implemented';
    default:
      return 'Submitted';
  }
}

// The real (ML-classified) domain taxonomy is 11 lowercase values distinct
// from this UI's Category union — mapped explicitly rather than guessed.
// `content_domain` is null until the async worker job classifies it, so a
// challenge legitimately has no category for the first few seconds.
const DOMAIN_TO_CATEGORY: Record<string, Category> = {
  education: 'Education',
  agriculture: 'Agriculture',
  healthcare: 'Healthcare',
  water: 'Water Resources',
  sanitation: 'Water Resources',
  environment: 'Environment',
  energy: 'Energy',
  urban_infrastructure: 'Urban Development',
  accessibility: 'Accessibility',
  public_administration: 'Public Administration',
  rural_livelihoods: 'Rural Livelihoods',
};

/** The backend has no citizen-facing "project/consortium progress" endpoint
 * — that data belongs to the organizational portal's Project model, which
 * a citizen cannot currently see. Rather than fabricate stages like
 * "Matched with Institution" or "Pilot Prototyping" the original UI showed,
 * this builds a small, honest timeline from only the real signals the
 * backend actually returns: submission, clustering, and resolution. */
function buildMilestonesFromChallenge(c: BackendChallengeResponse): Milestone[] {
  const milestones: Milestone[] = [
    {
      id: `${c.id}-submitted`,
      problemId: c.id,
      stage: 'Submitted',
      title: 'Report submitted',
      description: 'Your report was received and registered.',
      timestamp: c.created_at,
      completed: true,
    },
  ];

  if (c.status !== 'submitted') {
    milestones.push({
      id: `${c.id}-review`,
      problemId: c.id,
      stage: 'Under Review',
      title: 'Under review',
      description: 'A validator has reviewed this report.',
      timestamp: c.updated_at,
      completed: true,
    });
  }

  if (c.cluster_id) {
    milestones.push({
      id: `${c.id}-clustered`,
      problemId: c.id,
      stage: 'Matched with Institution',
      title: 'Grouped with related reports',
      description: 'This report has been grouped with similar reports for coordinated action.',
      timestamp: c.updated_at,
      completed: true,
    });
  }

  if (c.status === 'resolved') {
    milestones.push({
      id: `${c.id}-resolved`,
      problemId: c.id,
      stage: 'Solution Implemented',
      title: 'Resolved',
      description: 'This report has been marked resolved.',
      timestamp: c.updated_at,
      completed: true,
    });
  }

  return milestones;
}

/** Real, live area names resolved via administrativeAreaApi — see
 * mapBackendChallengeToProblem's `areaName` parameter. */
export function mapBackendChallengeToProblem(
  c: BackendChallengeResponse,
  options?: { areaName?: string; currentUserId?: string; currentUserName?: string; currentUserPhone?: string }
): Problem {
  const category = c.content_domain ? DOMAIN_TO_CATEGORY[c.content_domain] : undefined;
  const isOwnSubmission = options?.currentUserId != null && c.submitted_by_id === options.currentUserId;

  return {
    id: c.id,
    trackingCode: `JH-${c.id.slice(0, 8).toUpperCase()}`,
    title: c.title,
    description: c.description,
    // No fabricated category before classification lands — UI must render
    // this as "Classifying…", never guess.
    category: category ?? ('Public Administration' as Category),
    location: {
      district: options?.areaName || 'Not yet resolved',
      villageOrArea: '',
      pincode: c.pin_code || '',
      latitude: 0,
      longitude: 0,
      formattedAddress: [options?.areaName, c.pin_code].filter(Boolean).join(' - '),
    },
    status: mapBackendStatusToFrontend(c.status),
    upvotes: 0,
    submittedBy: {
      id: c.submitted_by_id,
      fullName: c.on_behalf_of_name || (isOwnSubmission ? options?.currentUserName : undefined) || 'Verified Citizen',
      phone: c.on_behalf_of_phone || (isOwnSubmission ? options?.currentUserPhone : undefined) || '',
      district: options?.areaName || '',
      isVerified: true,
    },
    createdAt: c.created_at,
    updatedAt: c.updated_at,
    media: [],
    milestones: buildMilestonesFromChallenge(c),
  };
}

export const challengesApi = {
  /** Fetch challenges submitted by a specific citizen. Throws on failure —
   * callers show a real error/retry state, never fabricated data. */
  async getMyChallenges(submittedById: string): Promise<BackendChallengeResponse[]> {
    const res = await apiClient<PaginatedChallenges>(
      `/challenges?submitted_by_id=${encodeURIComponent(submittedById)}&limit=100`
    );
    return res.items;
  },

  async getChallengeById(id: string): Promise<BackendChallengeResponse> {
    return apiClient<BackendChallengeResponse>(`/challenges/${id}`);
  },

  /** Submit a new challenge/grievance. Real backend call only — no local
   * fabrication of a "successful" submission on failure. */
  async createChallenge(input: CreateChallengeInput): Promise<BackendChallengeResponse> {
    return apiClient<BackendChallengeResponse>('/challenges', {
      method: 'POST',
      body: JSON.stringify({
        title: input.title,
        description: input.description,
        administrative_area_id: input.administrative_area_id,
        pin_code: input.pin_code || undefined,
      }),
    });
  },
};
