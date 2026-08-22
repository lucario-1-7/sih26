# End-to-End Tests

These tests exercise the **fully running stack** (server + ML service +
Postgres + Redis + ARQ worker) over real HTTP — as opposed to
`server/tests/integration`, which uses an in-process ASGI transport and
therefore doesn't exercise the actual worker process or network boundaries.

## Prerequisites

The whole stack must already be running and reachable, e.g.:

```
docker compose up --build
# then, in another shell, apply migrations (see database/README.md)
```

or the local (non-Docker) equivalent from the root README.

## Running

```
pip install httpx pytest
SERVER_BASE_URL=http://localhost:8000/api/v1 python -m pytest tests/e2e -q
```

Tests skip (not fail) if `SERVER_BASE_URL` is unreachable, so they're safe
to leave in a CI job that doesn't always have the full stack up.
