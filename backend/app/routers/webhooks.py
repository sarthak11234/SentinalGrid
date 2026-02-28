"""
Webhook endpoints for receiving replies.
- Manual reply input (prototype workaround)
- Email inbound parse (stretch goal)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DataRow
from app.schemas import ManualReplyInput
from app.agent import process_reply
from app.config import get_settings

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


@router.post("/email")
async def email_webhook(
    db: Session = Depends(get_db),
):
    """
    Placeholder for email inbound parse webhook (SendGrid / Mailgun).
    TODO: Implement when deploying with a real domain.
    """
    return {"message": "Email webhook endpoint ready — not yet configured"}
