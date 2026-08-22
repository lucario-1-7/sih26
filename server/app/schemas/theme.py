import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ThemeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(..., min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)


class ThemeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)


class ThemeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
