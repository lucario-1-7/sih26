import uuid

import pytest
from fastapi import HTTPException

from app.core.rbac import require_role
from app.models.enums import Role
from app.models.user import User


def _user(role: Role) -> User:
    return User(id=uuid.uuid4(), phone="+911234567890", name="Test", role=role, is_active=True)


@pytest.mark.asyncio
async def test_require_role_allows_matching_role():
    dependency = require_role(Role.ADMIN)
    user = _user(Role.ADMIN)
    result = await dependency(user=user)
    assert result is user


@pytest.mark.asyncio
async def test_require_role_denies_non_matching_role():
    dependency = require_role(Role.ADMIN)
    user = _user(Role.CITIZEN)
    with pytest.raises(HTTPException) as exc_info:
        await dependency(user=user)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_role_allows_any_of_multiple_roles():
    dependency = require_role(Role.OFFICER, Role.ADMIN)
    user = _user(Role.OFFICER)
    result = await dependency(user=user)
    assert result is user
