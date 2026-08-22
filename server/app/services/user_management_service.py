import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import VALID_DOMAIN_ROLES, Domain, Role
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "User not found", "code": "NOT_FOUND"}
)
PHONE_TAKEN = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={"detail": "A user with this phone number already exists", "code": "CONFLICT"},
)
INVALID_DOMAIN_ROLE = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"detail": "role is not valid for the given domain", "code": "INVALID_DOMAIN_ROLE"},
)
ORG_NOT_FOUND = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={
        "detail": "organization_id does not reference an existing organization",
        "code": "INVALID_ORGANIZATION",
    },
)
ORG_REQUIRED = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"detail": "organization_id is required for this domain", "code": "ORGANIZATION_REQUIRED"},
)
SELF_MODIFICATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={
        "detail": "Cannot change your own role, domain, or organization",
        "code": "SELF_MODIFICATION_FORBIDDEN",
    },
)


def _validate_domain_role(domain: Domain, role: Role) -> None:
    if role not in VALID_DOMAIN_ROLES.get(domain, frozenset()):
        raise INVALID_DOMAIN_ROLE


async def _validate_organization(db: AsyncSession, domain: Domain, organization_id: uuid.UUID | None) -> None:
    if domain in (Domain.UNIVERSITY, Domain.INDUSTRY):
        if organization_id is None:
            raise ORG_REQUIRED
    if organization_id is not None:
        org = await OrganizationRepository(db).get(organization_id)
        if org is None:
            raise ORG_NOT_FOUND


async def create_user(db: AsyncSession, *, data: UserCreate, actor: User) -> User:
    """Provisions a login for a staff member. The new user's phone number is
    the OTP login identifier — Superadmin does not set a password; the user
    authenticates through the existing OTP flow once created."""
    _validate_domain_role(data.domain, data.role)
    await _validate_organization(db, data.domain, data.organization_id)

    user_repo = UserRepository(db)
    if await user_repo.get_by_phone(data.phone) is not None:
        raise PHONE_TAKEN

    user = await user_repo.create(
        phone=data.phone,
        name=data.name,
        role=data.role,
        domain=data.domain,
        organization_id=data.organization_id,
        administrative_area_id=data.administrative_area_id,
    )
    await AuditRepository(db).log(
        user_id=actor.id,
        action="user.create",
        entity_type="user",
        entity_id=user.id,
        meta={
            "role": data.role.value,
            "domain": data.domain.value,
            "organization_id": str(data.organization_id) if data.organization_id else None,
        },
    )
    await db.commit()
    return user


async def update_user(db: AsyncSession, user_id: uuid.UUID, *, data: UserUpdate, actor: User) -> User:
    """Role/domain/organization/active-status management. A user (including a
    Superadmin) can never modify their own role, domain, or organization
    through this endpoint — that would be a self-service privilege escalation
    path. `is_active` and `name` may still be self-managed if ever needed."""
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    if user is None:
        raise NOT_FOUND

    escalation_fields_set = data.role is not None or data.domain is not None or data.organization_id is not None
    if user_id == actor.id and escalation_fields_set:
        raise SELF_MODIFICATION_FORBIDDEN

    new_role = data.role if data.role is not None else user.role
    new_domain = data.domain if data.domain is not None else user.domain
    if data.role is not None or data.domain is not None:
        _validate_domain_role(new_domain, new_role)

    new_organization_id = data.organization_id if data.organization_id is not None else user.organization_id
    if data.role is not None or data.domain is not None or data.organization_id is not None:
        await _validate_organization(db, new_domain, new_organization_id)

    changes: dict = {}
    if data.name is not None:
        user.name = data.name
        changes["name"] = data.name
    if data.role is not None:
        user.role = data.role
        changes["role"] = data.role.value
    if data.domain is not None:
        user.domain = data.domain
        changes["domain"] = data.domain.value
    if data.organization_id is not None:
        user.organization_id = data.organization_id
        changes["organization_id"] = str(data.organization_id)
    if data.administrative_area_id is not None:
        user.administrative_area_id = data.administrative_area_id
        changes["administrative_area_id"] = str(data.administrative_area_id)
    if data.is_active is not None:
        user.is_active = data.is_active
        changes["is_active"] = data.is_active

    await AuditRepository(db).log(
        user_id=actor.id, action="user.update", entity_type="user", entity_id=user.id, meta=changes
    )
    await db.commit()
    await db.refresh(user)  # onupdate=now() is server-computed — refresh before serializing
    return user
