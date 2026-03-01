"""
Webhook endpoints for receiving replies.
- Manual reply input (prototype workaround)
- WAHA WhatsApp inbound webhook
- Email inbound parse (stretch goal)
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DataRow
from app.schemas import ManualReplyInput
from app.agent import process_reply
from app.config import get_settings
from app.messaging import send_whatsapp

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/manual-reply")
async def manual_reply(
    payload: ManualReplyInput,
    db: Session = Depends(get_db),
):
    """
    Process a manually entered reply (prototype workaround).
    In production this would be triggered by a WhatsApp/Email webhook.
    """
    row = db.query(DataRow).filter(DataRow.id == payload.data_row_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Data row not found")

    if not row.outbound_message:
        raise HTTPException(status_code=400, detail="No outbound message was sent for this row")

    # Use the agent to process the reply
    result = process_reply(
        original_row_data=row.row_data,
        outbound_message=row.outbound_message,
        reply_text=payload.reply_text,
    )

    settings = get_settings()
    row.reply_text = payload.reply_text
    row.confidence = result.get("confidence", 0)
    row.suggested_update = result.get("updates", {})

    if result.get("confidence", 0) >= settings.confidence_threshold:
        # Auto-update the row data
        updated = {**row.row_data, **result.get("updates", {})}
        row.row_data = updated
        row.message_status = "replied"
        row.needs_review = False
    else:
        # Flag for human review
        row.message_status = "review"
        row.needs_review = True

    db.commit()

    return {
        "message": "Reply processed",
        "intent": result.get("intent"),
        "confidence": result.get("confidence"),
        "needs_review": row.needs_review,
        "suggested_update": result.get("updates"),
    }


# ════════════════════════════════════════════════
# WAHA WhatsApp Inbound Webhook
# ════════════════════════════════════════════════

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Receive inbound WhatsApp messages from WAHA.
    WAHA sends POST requests when messages arrive.
    Configure WAHA webhook URL: http://localhost:8000/webhooks/whatsapp
    """
    try:
        body = await request.json()
    except Exception:
        return {"status": "ignored", "reason": "Invalid JSON"}

    # WAHA sends different event types
    event = body.get("event", "")

    # Only process incoming messages
    if event != "message":
        return {"status": "ignored", "reason": f"Event type '{event}' not handled"}

    payload = body.get("payload", {})
    message_body = payload.get("body", "")
    from_number = payload.get("from", "")

    if not message_body or not from_number:
        return {"status": "ignored", "reason": "Empty message or sender"}

    # Clean the phone number (remove @c.us suffix from WAHA)
    phone = from_number.replace("@c.us", "").replace("@s.whatsapp.net", "")

    # Find matching data rows by phone number
    rows = db.query(DataRow).filter(
        DataRow.contact_phone.isnot(None),
        DataRow.message_status == "sent",
    ).all()

    matched_row = None
    for row in rows:
        if row.contact_phone and phone.endswith(row.contact_phone[-10:]):
            matched_row = row
            break

    if not matched_row:
        return {"status": "no_match", "phone": phone, "message": "No matching sent row found"}

    # Process the reply with AI
    result = process_reply(
        original_row_data=matched_row.row_data,
        outbound_message=matched_row.outbound_message or "",
        reply_text=message_body,
    )

    settings = get_settings()
    matched_row.reply_text = message_body
    matched_row.confidence = result.get("confidence", 0)
    matched_row.suggested_update = result.get("updates", {})

    if result.get("confidence", 0) >= settings.confidence_threshold:
        updated = {**matched_row.row_data, **result.get("updates", {})}
        matched_row.row_data = updated
        matched_row.message_status = "replied"
        matched_row.needs_review = False
    else:
        matched_row.message_status = "review"
        matched_row.needs_review = True

    db.commit()

    return {
        "status": "processed",
        "row_id": matched_row.id,
        "intent": result.get("intent"),
        "confidence": result.get("confidence"),
    }


# ════════════════════════════════════════════════
# Quick Send (one-off messages)
# ════════════════════════════════════════════════

@router.post("/send-whatsapp")
async def quick_send_whatsapp(request: Request):
    """Send a quick one-off WhatsApp message (not tied to a campaign)."""
    body = await request.json()
    phone = body.get("phone", "")
    message = body.get("message", "")

    if not phone or not message:
        raise HTTPException(status_code=400, detail="phone and message are required")

    success = send_whatsapp(to=phone, body=message)
    return {
        "success": success,
        "phone": phone,
        "message": "Sent" if success else "Failed to send",
    }


# ════════════════════════════════════════════════
# WAHA Status Check
# ════════════════════════════════════════════════

@router.get("/whatsapp-status")
async def whatsapp_status():
    """Check if WAHA is connected and session is active."""
    import httpx
    settings = get_settings()

    try:
        headers = {}
        if settings.waha_api_key:
            headers["X-Api-Key"] = str(settings.waha_api_key)

        resp = httpx.get(
            f"{settings.waha_url}/api/sessions/{settings.waha_session}",
            headers=headers,
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "connected": True,
                "status": data.get("status", "unknown"),
                "name": data.get("name", ""),
            }
        else:
            return {"connected": False, "status": "error", "detail": resp.text}
    except Exception as e:
        return {"connected": False, "status": "offline", "detail": str(e)}


@router.post("/email")
async def email_webhook(
    db: Session = Depends(get_db),
):
    """
    Placeholder for email inbound parse webhook (SendGrid / Mailgun).
    TODO: Implement when deploying with a real domain.
    """
    return {"message": "Email webhook endpoint ready — not yet configured"}
