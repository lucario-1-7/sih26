from enum import StrEnum


class Role(StrEnum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    ANALYST = "analyst"
    ADMIN = "admin"


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
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


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
