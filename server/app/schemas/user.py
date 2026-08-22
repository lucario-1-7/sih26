import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Role


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone: str
    name: str
    role: Role
    administrative_area_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
