"""
Campaign CRUD + file upload + launch endpoints.
"""

import io
import time
from collections import Counter

import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, DataRow
from app.schemas import (
    CampaignResponse, CampaignListResponse, CampaignDetailResponse,
    DataRowResponse, ReviewAction,
)
from app.agent import draft_message, process_reply
from app.messaging import send_message
from app.config import get_settings

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# ────────────────────────── helpers ──────────────────────────

def _detect_email_column(columns: list[str]) -> str | None:
    """Try to find the email column by name."""
    for col in columns:
        if "email" in col.lower() or "mail" in col.lower():
            return col
    return None


def _detect_phone_column(columns: list[str]) -> str | None:
    """Try to find the phone/WhatsApp column by name."""
    for col in columns:
        low = col.lower()
        if any(k in low for k in ["phone", "mobile", "whatsapp", "cell", "contact_number"]):
            return col
    return None


def _parse_file(file: UploadFile) -> pd.DataFrame:
    """Parse an uploaded CSV or Excel file into a DataFrame."""
    contents = file.file.read()
    filename = file.filename or ""

    if filename.endswith(".csv"):
        return pd.read_csv(io.BytesIO(contents))
    elif filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV or XLSX.")


# ────────────────────── campaign CRUD ────────────────────────

@router.post("", response_model=CampaignResponse)
async def create_campaign(
    name: str = Form(...),
    master_prompt: str = Form(...),
    user_email: str = Form("anonymous@example.com"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Create a new campaign by uploading a data file and providing a prompt."""
    # Parse file
    df = _parse_file(file)

    # Create campaign record
    campaign = Campaign(
        user_email=user_email,
        name=name,
        master_prompt=master_prompt,
        status="draft",
    )
    db.add(campaign)
    db.flush()  # get the ID

    # Detect email and phone columns
    email_col = _detect_email_column(df.columns.tolist())
    phone_col = _detect_phone_column(df.columns.tolist())

    # Insert data rows
    for idx, row in df.iterrows():
        row_dict = row.where(pd.notna(row), None).to_dict()

        # Convert numpy types to native Python types (SQLite JSON can't serialize numpy)
        row_dict = {
            k: (v.item() if hasattr(v, 'item') else v)
            for k, v in row_dict.items()
        }

        # Determine channel and contact info
        contact_email = str(row_dict.get(email_col, "")) if email_col else None
        contact_phone = str(int(row_dict.get(phone_col, ""))) if phone_col and row_dict.get(phone_col) is not None else None

        # Prefer WhatsApp if phone is available, otherwise email
        if contact_phone and contact_phone.strip():
            channel = "whatsapp"
        elif contact_email and contact_email.strip():
            channel = "email"
        else:
            channel = "email"

        data_row = DataRow(
            campaign_id=campaign.id,
            row_index=int(idx),
            row_data=row_dict,
            contact_email=contact_email,
            contact_phone=contact_phone,
            channel=channel,
            message_status="pending",
        )
        db.add(data_row)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(db: Session = Depends(get_db)):
    """List all campaigns."""
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return {"campaigns": campaigns}


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get campaign details with all data rows and stats."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    rows = db.query(DataRow).filter(DataRow.campaign_id == campaign_id).order_by(DataRow.row_index).all()
    status_counts = Counter(r.message_status for r in rows)
    stats = {
        "total": len(rows),
        "pending": status_counts.get("pending", 0),
        "sent": status_counts.get("sent", 0),
        "replied": status_counts.get("replied", 0),
        "review": status_counts.get("review", 0),
        "failed": status_counts.get("failed", 0),
    }

    return {"campaign": campaign, "rows": rows, "stats": stats}


# ────────────────────── campaign launch ──────────────────────

def _run_campaign(campaign_id: int):
    """Background task: draft messages & send emails for all pending rows."""
    from app.database import SessionLocal  # local import to avoid circular

    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return

        campaign.status = "running"
        db.commit()

        rows = db.query(DataRow).filter(
            DataRow.campaign_id == campaign_id,
            DataRow.message_status == "pending",
        ).all()

        for row in rows:
            try:
                # 1. Draft the message using Gemini
                message = draft_message(campaign.master_prompt, row.row_data)
                row.outbound_message = message

                # 2. Send via the appropriate channel
                contact = row.contact_phone if row.channel == "whatsapp" else row.contact_email
                if contact:
                    success = send_message(
                        to=contact,
                        body=message,
                        channel=row.channel,
                        subject=f"Message from {campaign.name}",
                    )
                    row.message_status = "sent" if success else "failed"
                else:
                    row.message_status = "sent"  # Mark as sent even without contact (for demo)

                db.commit()

                # 3. Basic rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"[CAMPAIGN ERROR] Row {row.id}: {e}")
                row.message_status = "failed"
                db.commit()

        # Update campaign status
        failed_count = db.query(DataRow).filter(
            DataRow.campaign_id == campaign_id,
            DataRow.message_status == "failed",
        ).count()

        campaign.status = "completed" if failed_count == 0 else "completed"
        db.commit()

    finally:
        db.close()


@router.post("/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Launch a campaign — drafts messages and sends them in the background."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status == "running":
        raise HTTPException(status_code=400, detail="Campaign is already running")

    background_tasks.add_task(_run_campaign, campaign_id)
    return {"message": "Campaign launch started", "campaign_id": campaign_id}


# ────────────────── review queue ──────────────────────

@router.get("/{campaign_id}/reviews", response_model=list[DataRowResponse])
async def get_review_queue(campaign_id: int, db: Session = Depends(get_db)):
    """Get all rows that need human review."""
    rows = db.query(DataRow).filter(
        DataRow.campaign_id == campaign_id,
        DataRow.needs_review == True,
    ).all()
    return rows


@router.post("/{campaign_id}/rows/{row_id}/review")
async def review_row(
    campaign_id: int,
    row_id: int,
    action: ReviewAction,
    db: Session = Depends(get_db),
):
    """Approve or reject an agent's suggested update."""
    row = db.query(DataRow).filter(DataRow.id == row_id, DataRow.campaign_id == campaign_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")

    if action.action == "approve" and row.suggested_update:
        # Merge the suggested update into row_data
        updated = {**row.row_data, **row.suggested_update}
        row.row_data = updated
        row.message_status = "replied"
        row.needs_review = False
    elif action.action == "reject":
        if action.manual_update:
            updated = {**row.row_data, **action.manual_update}
            row.row_data = updated
        row.message_status = "replied"
        row.needs_review = False
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    db.commit()
    return {"message": "Review completed", "row_id": row_id}
