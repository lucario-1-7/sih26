# Sahyog Mobile (Flutter)

Scaffold only — implementation intentionally deferred until the backend API
contracts under `/api/v1` are stable (per project instructions).

Planned structure once implementation begins:

```
mobile/
  lib/
    api/           # typed client for /api/v1, no duplicated business logic
    features/
      auth/
      challenges/
    widgets/
```

Scope is limited to citizen-facing flows actually required by the project
(OTP login, challenge submission, challenge status) — no reviewer/admin
screens on mobile unless a requirement specifies them.
