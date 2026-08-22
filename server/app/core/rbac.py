from fastapi import Depends, HTTPException, status

from app.api.v1.auth.dependencies import get_current_user
from app.models.enums import Role
from app.models.user import User


def require_role(*roles: Role):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Insufficient role for this action", "code": "FORBIDDEN"},
            )
        return user

    return dependency
