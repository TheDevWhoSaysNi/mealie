#!/usr/bin/env python3
"""Create a dedicated Mealie automation user and long-lived API token.

Run on the VPS (localhost) so admin credentials never leave the server:

  export MEALIE_ADMIN_USERNAME=admin
  export MEALIE_ADMIN_PASSWORD='...'
  export MEALIE_BASE_URL=http://127.0.0.1:9925
  export MEALIE_PUBLIC_BASE_URL=https://recipes.example.com
  python3 scripts/create-grokbot-user.py

Writes secrets to ../grokbot-credentials.json (gitignored) with mode 0600.
"""
from __future__ import annotations

import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

INSTALL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUT = INSTALL_DIR / "grokbot-credentials.json"

BASE = os.environ.get("MEALIE_BASE_URL", "http://127.0.0.1:9925").rstrip("/")
PUBLIC = os.environ.get("MEALIE_PUBLIC_BASE_URL", "").rstrip("/")
ADMIN_USER = os.environ.get("MEALIE_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("MEALIE_ADMIN_PASSWORD")
BOT_USERNAME = os.environ.get("MEALIE_BOT_USERNAME", "grokbot-food")
BOT_EMAIL = os.environ.get("MEALIE_BOT_EMAIL", "grokbot-food@mealie.local")
BOT_FULL_NAME = os.environ.get("MEALIE_BOT_FULL_NAME", "GrokBot Food")
TOKEN_NAME = os.environ.get("MEALIE_BOT_TOKEN_NAME", "grokbot-food")
INTEGRATION_ID = os.environ.get("MEALIE_BOT_INTEGRATION_ID", "grokbot")


def auth(username: str, password: str) -> str:
    data = urllib.parse.urlencode({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/auth/token",
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["access_token"]


def request_json(
    method: str, path: str, token: str, payload: dict | None = None
) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main() -> int:
    if not ADMIN_PASSWORD:
        print("Set MEALIE_ADMIN_PASSWORD (Mealie admin login).", file=sys.stderr)
        return 1

    admin_token = auth(ADMIN_USER, ADMIN_PASSWORD)
    bot_password = secrets.token_urlsafe(24)

    try:
        user = request_json(
            "POST",
            "/api/admin/users",
            admin_token,
            {
                "username": BOT_USERNAME,
                "email": BOT_EMAIL,
                "fullName": BOT_FULL_NAME,
                "password": bot_password,
                "admin": False,
                "advanced": True,
            },
        )
    except urllib.error.HTTPError as err:
        if err.code not in (400, 409, 422):
            print(err.read().decode(), file=sys.stderr)
            return err.code
        user = None

    if user is None:
        # User may already exist; reset password via admin update if you need a new password.
        users = request_json("GET", "/api/admin/users", admin_token)
        matches = [u for u in users["items"] if u.get("username") == BOT_USERNAME]
        if not matches:
            print("Could not create or find bot user.", file=sys.stderr)
            return 1
        uid = matches[0]["id"]
        detail = request_json("GET", f"/api/admin/users/{uid}", admin_token)
        detail["password"] = bot_password
        detail["canOrganize"] = True
        detail["canManageHousehold"] = True
        detail["advanced"] = True
        user = request_json("PUT", f"/api/admin/users/{uid}", admin_token, detail)
    else:
        uid = user["id"]
        detail = request_json("GET", f"/api/admin/users/{uid}", admin_token)
        detail["canOrganize"] = True
        detail["canManageHousehold"] = True
        detail["advanced"] = True
        user = request_json("PUT", f"/api/admin/users/{uid}", admin_token, detail)

    bot_token = auth(BOT_USERNAME, bot_password)
    token_resp = request_json(
        "POST",
        "/api/users/api-tokens",
        bot_token,
        {"name": TOKEN_NAME, "integrationId": INTEGRATION_ID},
    )

    out_path = Path(os.environ.get("MEALIE_BOT_CREDENTIALS_FILE", DEFAULT_OUT))
    payload = {
        "username": BOT_USERNAME,
        "password": bot_password,
        "api_token": token_resp["token"],
        "base_url": PUBLIC or BASE,
        "api_docs": f"{PUBLIC or BASE}/docs",
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_path.chmod(0o600)
    print(f"Wrote {out_path}")
    print("Give api_token to GrokBot; keep password for recovery only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
