import uuid

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository):
    async def log(
        self,
        *,
        user_id: uuid.UUID | None,
        action: str,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        meta: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            meta=meta,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry
