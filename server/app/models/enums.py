from enum import StrEnum


class Domain(StrEnum):
    """Organizational domain a user belongs to. Every Role maps to exactly one
    Domain — see VALID_DOMAIN_ROLES below, enforced by a DB CHECK constraint."""

    CITIZEN = "citizen"
    GOVERNMENT = "government"
    UNIVERSITY = "university"
    INDUSTRY = "industry"
    SUPERADMIN = "superadmin"


class Role(StrEnum):
    CITIZEN = "citizen"
    # GOVERNMENT domain
    VALIDATOR = "validator"
    FIELD_ASSISTANT = "field_assistant"
    # UNIVERSITY domain
    COORDINATOR = "coordinator"
    FACULTY = "faculty"
    # INDUSTRY domain
    INDUSTRY = "industry"
    # SUPERADMIN domain
    SUPERADMIN = "superadmin"


# Single source of truth for valid (domain, role) combinations — mirrored by a
# DB CHECK constraint (see the domain/role alignment migration) so invalid
# combinations are rejected even if application-level validation is bypassed.
VALID_DOMAIN_ROLES: dict[Domain, frozenset[Role]] = {
    Domain.CITIZEN: frozenset({Role.CITIZEN}),
    Domain.GOVERNMENT: frozenset({Role.VALIDATOR, Role.FIELD_ASSISTANT}),
    Domain.UNIVERSITY: frozenset({Role.COORDINATOR, Role.FACULTY}),
    Domain.INDUSTRY: frozenset({Role.INDUSTRY}),
    Domain.SUPERADMIN: frozenset({Role.SUPERADMIN}),
}


class ChallengeSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AdministrativeLevel(StrEnum):
    STATE = "state"
    DISTRICT = "district"
    BLOCK = "block"
    GP = "gp"
    VILLAGE = "village"


class ChallengeStatus(StrEnum):
    SUBMITTED = "submitted"
    OPEN = "open"
    DUPLICATE = "duplicate"
    RESOLVED = "resolved"


class ClusterStatus(StrEnum):
    ACTIVE = "active"
    RESOLVED = "resolved"


class ProjectStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Valid forward transitions for Project.status. CANCELLED is reachable from
# any non-terminal state (handled separately in project_service, not listed
# per-row here to avoid repeating it five times).
PROJECT_STATUS_TRANSITIONS: dict[ProjectStatus, frozenset[ProjectStatus]] = {
    ProjectStatus.PROPOSED: frozenset({ProjectStatus.ACCEPTED, ProjectStatus.CANCELLED}),
    ProjectStatus.ACCEPTED: frozenset({ProjectStatus.ACTIVE, ProjectStatus.CANCELLED}),
    ProjectStatus.ACTIVE: frozenset({ProjectStatus.ON_HOLD, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED}),
    ProjectStatus.ON_HOLD: frozenset({ProjectStatus.ACTIVE, ProjectStatus.CANCELLED}),
    ProjectStatus.COMPLETED: frozenset(),
    ProjectStatus.CANCELLED: frozenset(),
}


class MilestoneStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class DeliverableStatus(StrEnum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DuplicateDecisionType(StrEnum):
    DUPLICATE = "duplicate"
    NOT_DUPLICATE = "not_duplicate"


class OrganizationType(StrEnum):
    UNIVERSITY = "university"
    INDUSTRY = "industry"


class ConsortiumStatus(StrEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    DISSOLVED = "dissolved"


class CollaborationType(StrEnum):
    FUNDING = "funding"
    MENTORING = "mentoring"
    EQUIPMENT = "equipment"
    TECHNICAL_SUPPORT = "technical_support"
    PILOT_SUPPORT = "pilot_support"
    OTHER = "other"


class CollaborationStatus(StrEnum):
    INTERESTED = "interested"
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"


COLLABORATION_STATUS_TRANSITIONS: dict[CollaborationStatus, frozenset[CollaborationStatus]] = {
    CollaborationStatus.INTERESTED: frozenset({CollaborationStatus.PROPOSED, CollaborationStatus.REJECTED}),
    CollaborationStatus.PROPOSED: frozenset({CollaborationStatus.ACCEPTED, CollaborationStatus.REJECTED}),
    CollaborationStatus.ACCEPTED: frozenset({CollaborationStatus.ACTIVE, CollaborationStatus.REJECTED}),
    CollaborationStatus.ACTIVE: frozenset({CollaborationStatus.COMPLETED}),
    CollaborationStatus.COMPLETED: frozenset(),
    CollaborationStatus.REJECTED: frozenset(),
}


class CommitmentStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    FULFILLED = "fulfilled"
    REJECTED = "rejected"


class SolutionStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
