// Typed mirrors of the backend's Pydantic response schemas (see
// server/app/schemas/*.py and GET /api/v1/openapi.json). Keep in sync with
// the backend contract — do not invent fields that don't exist there.

export type Domain = "citizen" | "government" | "university" | "industry" | "superadmin";

export type Role =
  | "citizen"
  | "validator"
  | "field_assistant"
  | "coordinator"
  | "faculty"
  | "industry"
  | "superadmin";

export interface PaginatedResponse<T> {
  items: T[];
  next_cursor: string | null;
  total: number | null;
}

export interface ApiErrorBody {
  detail: string;
  code: string;
  request_id?: string;
  errors?: unknown;
}

export interface UserResponse {
  id: string;
  phone: string;
  name: string;
  role: Role;
  domain: Domain;
  organization_id: string | null;
  administrative_area_id: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// --- Clusters (used as "Opportunities" — see lib/api/clusters.ts) ---

export type ClusterStatus = "active" | "resolved";

export interface ClusterResponse {
  id: string;
  title: string;
  description: string | null;
  theme_id: string | null;
  status: ClusterStatus;
  created_at: string;
  updated_at: string;
}

// --- Projects ---

export type ProjectStatus = "proposed" | "accepted" | "active" | "on_hold" | "completed" | "cancelled";

export const PROJECT_STATUS_TRANSITIONS: Record<ProjectStatus, ProjectStatus[]> = {
  proposed: ["accepted", "cancelled"],
  accepted: ["active", "cancelled"],
  active: ["on_hold", "completed", "cancelled"],
  on_hold: ["active", "cancelled"],
  completed: [],
  cancelled: [],
};

export interface ProjectResponse {
  id: string;
  cluster_id: string;
  title: string;
  description: string | null;
  status: ProjectStatus;
  owner_id: string;
  organization_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateInput {
  cluster_id: string;
  title: string;
  description?: string | null;
}

export interface ProjectUpdateInput {
  title?: string;
  description?: string | null;
  status?: ProjectStatus;
}

// --- Milestones ---

export type MilestoneStatus = "pending" | "in_progress" | "completed" | "blocked";

export interface MilestoneResponse {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  status: MilestoneStatus;
  completed_at: string | null;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface MilestoneCreateInput {
  title: string;
  description?: string | null;
  due_date?: string | null;
  order?: number;
}

export interface MilestoneUpdateInput {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  order?: number;
  status?: MilestoneStatus;
}

// --- Deliverables ---

export type DeliverableStatus = "pending" | "submitted" | "verified" | "rejected";

export interface DeliverableResponse {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  status: DeliverableStatus;
  evidence: string | null;
  submitted_at: string | null;
  verified_at: string | null;
  verified_by_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface DeliverableCreateInput {
  title: string;
  description?: string | null;
  due_date?: string | null;
}

export interface DeliverableUpdateInput {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  evidence?: string | null;
}

// --- Project participants (students — no accounts) ---

export interface ProjectParticipantResponse {
  id: string;
  project_id: string;
  name: string;
  department: string | null;
  academic_year: string | null;
  registration_id: string | null;
  participation_role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProjectParticipantCreateInput {
  name: string;
  department?: string | null;
  academic_year?: string | null;
  registration_id?: string | null;
  participation_role?: string;
}

export interface ProjectParticipantUpdateInput {
  name?: string;
  department?: string | null;
  academic_year?: string | null;
  registration_id?: string | null;
  participation_role?: string;
  is_active?: boolean;
}

// --- Solutions ---

export type SolutionStatus = "draft" | "published";

export interface SolutionResponse {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  outcome: string | null;
  status: SolutionStatus;
  created_at: string;
  updated_at: string;
}

export interface SolutionCreateInput {
  project_id: string;
  title: string;
  description?: string | null;
  outcome?: string | null;
}

export interface SolutionUpdateInput {
  title?: string;
  description?: string | null;
  outcome?: string | null;
  status?: SolutionStatus;
}

export interface ReplicationCandidateResponse {
  cluster_id: string;
  cluster_title: string;
  similarity: number;
}

// --- Impact indicators ---

export interface ImpactIndicatorResponse {
  id: string;
  project_id: string;
  name: string;
  unit: string;
  baseline_value: number | null;
  baseline_date: string | null;
  target_value: number | null;
  actual_value: number | null;
  endline_date: string | null;
  endline_evidence: string | null;
  verified_at: string | null;
  verified_by_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ImpactIndicatorCreateInput {
  name: string;
  unit: string;
  baseline_value?: number | null;
  baseline_date?: string | null;
  target_value?: number | null;
}

export interface ImpactIndicatorEndlineInput {
  actual_value: number;
  endline_date: string;
  endline_evidence?: string | null;
}

// --- Challenges ---

export type ChallengeStatus = "submitted" | "open" | "duplicate" | "resolved";
export type ChallengeSeverity = "low" | "medium" | "high" | "critical";

export interface ChallengeResponse {
  id: string;
  title: string;
  description: string;
  status: ChallengeStatus;
  severity: ChallengeSeverity | null;
  submitted_by_id: string;
  administrative_area_id: string;
  pin_code: string | null;
  cluster_id: string | null;
  duplicate_of_id: string | null;
  on_behalf_of_name: string | null;
  on_behalf_of_phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChallengeCreateInput {
  title: string;
  description: string;
  administrative_area_id: string;
  pin_code?: string | null;
  on_behalf_of_name?: string | null;
  on_behalf_of_phone?: string | null;
}

export interface ChallengeUpdateInput {
  title?: string;
  description?: string;
  severity?: ChallengeSeverity;
}

// --- Duplicate detection (human-in-the-loop; append-only decisions) ---

export interface DuplicateCandidateResponse {
  id: string;
  challenge_id: string;
  candidate_challenge_id: string;
  similarity_score: number;
  model_name: string;
  model_version: string;
  created_at: string;
}

export type DuplicateDecisionType = "duplicate" | "not_duplicate";

export interface DuplicateDecisionCreateInput {
  challenge_id: string;
  candidate_challenge_id: string;
  decision: DuplicateDecisionType;
  reason?: string | null;
}

export interface DuplicateDecisionResponse {
  id: string;
  challenge_id: string;
  candidate_challenge_id: string;
  decision: DuplicateDecisionType;
  reviewer_id: string;
  reason: string | null;
  created_at: string;
}

// --- Themes ---

export interface ThemeResponse {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface ThemeCreateInput {
  name: string;
  description?: string | null;
}

export interface ThemeUpdateInput {
  name?: string;
  description?: string | null;
}

export interface ClusterCreateInput {
  title: string;
  description?: string | null;
  theme_id?: string | null;
}

export interface ClusterUpdateInput {
  title?: string;
  description?: string | null;
  theme_id?: string | null;
  status?: ClusterStatus;
}

// --- Organizations ---

export type OrganizationType = "university" | "industry";

export interface OrganizationResponse {
  id: string;
  name: string;
  type: OrganizationType;
  domain_tags: string[];
  description: string | null;
  created_at: string;
}

export interface OrganizationCreateInput {
  name: string;
  type: OrganizationType;
  domain_tags?: string[];
  description?: string | null;
}

// --- Superadmin user management ---

export interface UserCreateInput {
  phone: string;
  name: string;
  role: Role;
  domain: Domain;
  organization_id?: string | null;
  administrative_area_id?: string | null;
}

export interface UserUpdateInput {
  name?: string;
  role?: Role;
  domain?: Domain;
  organization_id?: string | null;
  administrative_area_id?: string | null;
  is_active?: boolean;
}

// Mirrors the backend's VALID_DOMAIN_ROLES (server/app/models/enums.py) —
// single source of truth for which (domain, role) combinations the backend
// will accept. The backend still validates/enforces this; this is UX only
// (disabling invalid options in the create/edit form).
export const VALID_DOMAIN_ROLES: Record<Domain, Role[]> = {
  citizen: ["citizen"],
  government: ["validator", "field_assistant"],
  university: ["coordinator", "faculty"],
  industry: ["industry"],
  superadmin: ["superadmin"],
};

// --- Industry collaboration ---

export type CollaborationType = "funding" | "mentoring" | "equipment" | "technical_support" | "pilot_support" | "other";
export type CollaborationStatus = "interested" | "proposed" | "accepted" | "active" | "completed" | "rejected";

export const COLLABORATION_STATUS_TRANSITIONS: Record<CollaborationStatus, CollaborationStatus[]> = {
  interested: ["proposed", "rejected"],
  proposed: ["accepted", "rejected"],
  accepted: ["active", "rejected"],
  active: ["completed"],
  completed: [],
  rejected: [],
};

export interface CollaborationResponse {
  id: string;
  organization_id: string;
  project_id: string;
  type: CollaborationType;
  status: CollaborationStatus;
  proposal: string | null;
  created_at: string;
  updated_at: string;
}

export interface CollaborationCreateInput {
  project_id: string;
  type: CollaborationType;
  proposal?: string | null;
}

export interface CollaborationStatusUpdateInput {
  status: CollaborationStatus;
  proposal?: string | null;
}

export type CommitmentStatus = "proposed" | "accepted" | "fulfilled" | "rejected";

export interface CommitmentResponse {
  id: string;
  collaboration_id: string;
  type: CollaborationType;
  amount: number | null;
  currency: string | null;
  description: string | null;
  status: CommitmentStatus;
  evidence: string | null;
  created_at: string;
  updated_at: string;
}

export interface CommitmentCreateInput {
  type: CollaborationType;
  amount?: number | null;
  currency?: string | null;
  description?: string | null;
}

export interface CommitmentStatusUpdateInput {
  status: CommitmentStatus;
  evidence?: string | null;
}

// --- Matching / consortium ---

export interface MatchResult {
  organization_id: string;
  score: number;
  breakdown: Record<string, number>;
  rationale: string;
}

export type ConsortiumStatus = "proposed" | "confirmed" | "dissolved";

export interface ConsortiumResponse {
  id: string;
  project_id: string;
  status: ConsortiumStatus;
  created_at: string;
}

export interface ConsortiumMemberResponse {
  id: string;
  organization_id: string;
  role: string;
  match_score: number | null;
  rationale: string | null;
}

// --- Superadmin analytics ---

export interface ChallengeAnalytics {
  total: number;
  by_status: Record<string, number>;
  by_severity: Record<string, number>;
  by_administrative_area: Record<string, number>;
}

export interface ProjectAnalytics {
  total: number;
  by_status: Record<string, number>;
  by_organization: Record<string, number>;
}

export interface IndustryAnalytics {
  organization_count: number;
  collaboration_count: number;
  collaborations_by_status: Record<string, number>;
  commitments_by_status: Record<string, number>;
  commitments_by_type: Record<string, number>;
  funding_committed_by_currency: Record<string, number>;
}

export interface MLAnalytics {
  challenges_with_embedding: number;
  clusters_with_embedding: number;
  solutions_with_embedding: number;
  duplicate_candidates_generated: number;
  duplicate_decisions_total: number;
  duplicate_decisions_by_type: Record<string, number>;
}

export interface ModelInfo {
  model_name: string;
  embedding_dimension: number;
  duplicate_similarity_threshold: number;
  duplicate_candidate_limit: number;
  ml_service_url: string;
}
