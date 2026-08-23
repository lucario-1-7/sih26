"""Manual smoke test against the REAL, running backend + REAL MSG91 — never
run automatically, never run in CI. Requires:

  1. The backend stack up with ENVIRONMENT=production (or ENVIRONMENT=
     development with MSG91_WIDGET_ID/MSG91_TOKEN_AUTH set — either way, as
     long as the server process actually has real MSG91 credentials loaded).
  2. A real Indian mobile number you can read an SMS on right now.

This script never reads or writes credentials itself — it only calls the
backend's public HTTP API, exactly like the Flutter app or the organizational
web client would. It cannot leak the MSG91 auth key/token because it never
sees them.

Usage:
    python scripts/msg91_smoke_test.py +919876543210 [--base-url http://localhost:8000/api/v1]
"""

from __future__ import annotations

import argparse
import sys

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("phone", help="Real +91XXXXXXXXXX number to receive the SMS on")
    parser.add_argument("--base-url", default="http://localhost:8000/api/v1")
    args = parser.parse_args()

    if not args.phone.startswith("+91") or len(args.phone) != 13:
        print(f"error: phone must be in +91XXXXXXXXXX format, got {args.phone!r}", file=sys.stderr)
        return 1

    print(f"-> POST {args.base_url}/auth/otp/request  (phone={args.phone})")
    with httpx.Client(base_url=args.base_url, timeout=15.0) as client:
        resp = client.post("/auth/otp/request", json={"phone": args.phone})
        print(f"<- {resp.status_code} {resp.text}")
        if resp.status_code != 202:
            print("FAILED: OTP request did not return 202 — see response above.", file=sys.stderr)
            return 1

        print("\nCheck your phone for the real SMS from MSG91.")
        code = input("Enter the OTP you received: ").strip()

        print(f"\n-> POST {args.base_url}/auth/otp/verify  (phone={args.phone})")
        resp = client.post("/auth/otp/verify", json={"phone": args.phone, "code": code})
        # Never print the response body verbatim here — it contains real
        # access/refresh tokens for a real account.
        print(f"<- {resp.status_code}")
        if resp.status_code != 200:
            print(f"FAILED: verify did not return 200 (detail: {resp.json().get('detail', '')!r})", file=sys.stderr)
            return 1

        tokens = resp.json()
        if "access_token" not in tokens or "refresh_token" not in tokens:
            print("FAILED: 200 response but missing access_token/refresh_token", file=sys.stderr)
            return 1

        print("-> GET /users/me  (using the freshly issued access token)")
        resp = client.get("/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        print(f"<- {resp.status_code} {resp.json() if resp.status_code == 200 else resp.text}")
        if resp.status_code != 200:
            print("FAILED: /users/me did not accept the freshly issued token", file=sys.stderr)
            return 1

    print("\nPASS: real MSG91 SMS delivered, OTP verified by MSG91, JWT session established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
