import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import OrganizationType


class OrganizationSummary(BaseModel):
    """Minimal, read-only organization identity for embedding inside another
    resource's response (e.g. the university that has taken up a Project) -
    not the full OrganizationResponse (app.schemas.matching), which is for
    the organization resource itself."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    type: OrganizationType
