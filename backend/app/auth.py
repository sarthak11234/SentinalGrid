"""
Google OAuth 2.0 authentication.
- /auth/login  → redirects the user to Google's consent screen
- /auth/callback → exchanges the code for user info, issues a JWT
"""

import json
import hashlib
import hmac
import time
from base64 import urlsafe_b64encode, urlsafe_b64decode

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import httpx

from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

# ── Google OAuth endpoints ──
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


# ── Simple JWT helpers (no external lib needed) ──

def _create_token(payload: dict) -> str:
    """Create a simple HMAC-signed token (not full JWT, but enough for a prototype)."""
    settings = get_settings()
    payload["exp"] = int(time.time()) + 86400  # 24 hours
    data = urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(settings.secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()
    return f"{data}.{sig}"


def verify_token(token: str) -> dict | None:
    """Verify a token and return the payload, or None if invalid/expired."""
    settings = get_settings()
    try:
        data, sig = token.rsplit(".", 1)
        expected_sig = hmac.new(settings.secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(urlsafe_b64decode(data))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


# ── Routes ──

@router.get("/login")
async def login(request: Request):
    """Redirect user to Google's OAuth consent screen."""
    settings = get_settings()
    redirect_uri = str(request.url_for("auth_callback"))
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, code: str | None = None, error: str | None = None):
    """Exchange the authorization code for user info, issue a session token."""
    if error or not code:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error or 'no code'}")

    settings = get_settings()
    redirect_uri = str(request.url_for("auth_callback"))

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        })
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        tokens = token_resp.json()

        # Fetch user info
        userinfo_resp = await client.get(GOOGLE_USERINFO_URL, headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")
        user = userinfo_resp.json()

    # Create our own session token
    session_token = _create_token({
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    })

    # Redirect back to Streamlit with the token as a query param
    return RedirectResponse(f"{settings.frontend_url}?token={session_token}")
