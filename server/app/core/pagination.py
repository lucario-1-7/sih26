"""Keyset (cursor) pagination shared by every list endpoint.

Ordering is always (created_at DESC, id DESC) — created_at alone is not unique
enough to guarantee a stable order when two rows share a timestamp, so the
primary key is used as a tiebreaker. The cursor is an opaque, base64-encoded
token that carries the (created_at, id) of the last item on the page; the next
page is fetched with `WHERE (created_at, id) < (cursor_created_at, cursor_id)`
(row-wise comparison), which is why encode/decode round-trip both fields.
"""

from __future__ import annotations

import base64
import binascii
from datetime import datetime
from typing import Protocol, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

INVALID_CURSOR = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"detail": "Invalid or malformed pagination cursor", "code": "INVALID_CURSOR"},
)


class _HasCreatedAtAndId(Protocol):
    id: UUID
    created_at: datetime


ModelT = TypeVar("ModelT", bound=_HasCreatedAtAndId)


def encode_cursor(created_at: datetime, entity_id: UUID) -> str:
    raw = f"{created_at.isoformat()}|{entity_id}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
        created_at_str, id_str = raw.split("|", 1)
        return datetime.fromisoformat(created_at_str), UUID(id_str)
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise INVALID_CURSOR from exc


async def paginate(
    db: AsyncSession,
    stmt: Select,
    *,
    model: type[ModelT],
    limit: int,
    cursor: str | None,
) -> tuple[list[ModelT], str | None]:
    """Apply keyset pagination to `stmt`, which must already carry every filter
    but no ordering/limit/offset. Returns (page_items, next_cursor)."""
    if cursor is not None:
        cursor_created_at, cursor_id = decode_cursor(cursor)
        stmt = stmt.where(tuple_(model.created_at, model.id) < tuple_(cursor_created_at, cursor_id))

    stmt = stmt.order_by(model.created_at.desc(), model.id.desc()).limit(limit + 1)
    result = await db.execute(stmt)
    rows = list(result.scalars().all())

    items = rows[:limit]
    next_cursor = encode_cursor(items[-1].created_at, items[-1].id) if len(rows) > limit else None
    return items, next_cursor
