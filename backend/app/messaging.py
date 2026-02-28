"""
Messaging service — Email (SMTP) + WhatsApp (WAHA).
"""

import asyncio
from email.message import EmailMessage
import aiosmtplib
import httpx

from app.config import get_settings


# ════════════════════════════════════════════════
# EMAIL (Gmail SMTP)
# ════════════════════════════════════════════════

async def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email via SMTP."""
    settings = get_settings()

    msg = EmailMessage()
    msg["From"] = settings.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_pass,
            start_tls=True,
        )
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to}: {e}")
        return False


def send_email_sync(to: str, subject: str, body: str) -> bool:
    """Synchronous wrapper for send_email (used in BackgroundTasks)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(send_email(to, subject, body))
    finally:
        loop.close()


# ════════════════════════════════════════════════
# WHATSAPP via WAHA (self-hosted HTTP API)
# ════════════════════════════════════════════════

def send_whatsapp(to: str, body: str) -> bool:
    """
    Send a WhatsApp message via WAHA API.

    Args:
        to: Phone number with country code (e.g. "919876543210")
        body: Message text

    Returns:
        True if sent successfully, False otherwise.
    """
    settings = get_settings()

    # Normalize phone number — strip +, spaces, dashes
    phone = to.replace("+", "").replace(" ", "").replace("-", "")

    url = f"{settings.waha_url}/api/sendText"
    headers = {"Content-Type": "application/json"}
    if settings.waha_api_key:
        headers["X-Api-Key"] = settings.waha_api_key

    payload = {
        "chatId": f"{phone}@c.us",
        "text": body,
        "session": settings.waha_session,
    }

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 201 or resp.status_code == 200:
            return True
        else:
            print(f"[WAHA ERROR] Status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[WAHA ERROR] Failed to send to {to}: {e}")
        return False


# ════════════════════════════════════════════════
# UNIFIED SEND (auto-detect channel)
# ════════════════════════════════════════════════

def send_message(to: str, body: str, channel: str = "email", subject: str = "Message") -> bool:
    """
    Send a message via the appropriate channel.

    Args:
        to: Recipient (email address or phone number)
        body: Message body
        channel: "email" or "whatsapp"
        subject: Email subject (ignored for WhatsApp)
    """
    if channel == "whatsapp":
        return send_whatsapp(to, body)
    else:
        return send_email_sync(to, subject, body)
