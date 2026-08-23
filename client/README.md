# SocioSolve Web Client

Scaffold only, implementation intentionally deferred until the backend API
contracts under `/api/v1` are stable (per project instructions).

Planned structure once implementation begins:

```
client/
  src/
    api/          # typed client for /api/v1, no duplicated business logic
    features/
      auth/
      challenges/
      duplicate-review/
      projects/
      solutions/
      matching/
    components/
    routes/
```

Planned flows: OTP authentication, challenge submission/listing/detail,
duplicate-review queue (officer/admin only), project/solution views,
matching results.
