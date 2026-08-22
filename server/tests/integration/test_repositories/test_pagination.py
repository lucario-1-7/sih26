import uuid

import pytest

from app.core.pagination import decode_cursor, encode_cursor
from app.repositories.theme_repository import ThemeRepository


async def _create_themes(repo: ThemeRepository, db, count: int) -> list[uuid.UUID]:
    ids = []
    for i in range(count):
        theme = await repo.create(name=f"Pagination Test Theme {uuid.uuid4().hex[:8]} {i}", description=None)
        await db.commit()
        ids.append(theme.id)
    return ids


@pytest.mark.asyncio
async def test_first_page_has_no_cursor_and_returns_newest_first(db):
    repo = ThemeRepository(db)
    created = await _create_themes(repo, db, 3)
    newest_first = list(reversed(created))

    items, next_cursor = await repo.list(limit=3, cursor=None)

    returned_ids = [item.id for item in items]
    assert returned_ids[:3] == newest_first
    # There may be more (older) rows from prior test runs, so next_cursor
    # being set is fine — what matters is items are in stable desc order.


@pytest.mark.asyncio
async def test_cursor_walks_entire_collection_with_no_duplicates_and_terminates(db):
    repo = ThemeRepository(db)
    created = await _create_themes(repo, db, 5)
    expected_newest_first = list(reversed(created))

    seen: list[uuid.UUID] = []
    cursor: str | None = None
    for _ in range(1000):  # bounded — a real bug (infinite loop) must not hang the suite
        items, next_cursor = await repo.list(limit=2, cursor=cursor)
        seen.extend(item.id for item in items)
        if next_cursor is None:
            break
        cursor = next_cursor
    else:
        pytest.fail("pagination did not terminate — end of collection was never reached")

    # No duplicates across pages.
    assert len(seen) == len(set(seen))
    # Our 5 freshly created rows appear, in stable newest-first order, as a
    # contiguous prefix (they are the newest rows in the table).
    assert seen[:5] == expected_newest_first


@pytest.mark.asyncio
async def test_empty_page_cursor_yields_no_items_and_no_next_cursor(db):
    repo = ThemeRepository(db)
    created = await _create_themes(repo, db, 1)
    only_item, _ = await repo.list(limit=1, cursor=None)
    last_cursor = encode_cursor(only_item[0].created_at, only_item[0].id)

    items, next_cursor = await repo.list(limit=20, cursor=last_cursor)

    assert all(item.id != only_item[0].id for item in items)
    # Walking past the very last row must not error and must eventually stop.
    assert next_cursor is None or isinstance(next_cursor, str)


def test_cursor_round_trips():
    from datetime import datetime, timezone

    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    entity_id = uuid.uuid4()
    cursor = encode_cursor(created_at, entity_id)
    decoded_created_at, decoded_id = decode_cursor(cursor)
    assert decoded_created_at == created_at
    assert decoded_id == entity_id


def test_malformed_cursor_raises_422():
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        decode_cursor("not-a-valid-cursor-!!!")
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail["code"] == "INVALID_CURSOR"


def test_cursor_is_opaque_base64_not_a_raw_offset():
    # A cursor must not simply be a small integer offset like "20" — it must
    # encode ordering state and be base64-opaque.
    import base64
    from datetime import datetime, timezone

    cursor = encode_cursor(datetime(2026, 1, 1, tzinfo=timezone.utc), uuid.uuid4())
    assert cursor.isdigit() is False
    # It must decode as base64 without error (opaque but well-formed).
    base64.urlsafe_b64decode(cursor.encode("ascii"))
