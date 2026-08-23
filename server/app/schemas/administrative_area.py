import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import AdministrativeLevel


class AdministrativeAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    level: AdministrativeLevel
    lgd_code: str | None
    parent_id: uuid.UUID | None
