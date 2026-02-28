"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Any


# ── Campaign ──

class CampaignCreate(BaseModel):
    name: str
    master_prompt: str
    user_email: str = "anonymous@example.com"


class CampaignResponse(BaseModel):
    id: int
    user_email: str
    name: str
    master_prompt: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    campaigns: list[CampaignResponse]


# ── DataRow ──

class DataRowResponse(BaseModel):
    id: int
    campaign_id: int
    row_index: int
    row_data: dict[str, Any]
    contact_email: str | None
    contact_phone: str | None
    channel: str
    message_status: str
    outbound_message: str | None
    reply_text: str | None
    confidence: float | None
    needs_review: bool
    suggested_update: dict | None

    model_config = {"from_attributes": True}


class CampaignDetailResponse(BaseModel):
    campaign: CampaignResponse
    rows: list[DataRowResponse]
    stats: dict[str, int]  # e.g. {"pending": 5, "sent": 3, "replied": 1}


# ── Reply input (manual) ──

class ManualReplyInput(BaseModel):
    data_row_id: int
    reply_text: str


# ── Review actions ──

class ReviewAction(BaseModel):
    action: str  # "approve" | "reject"
    manual_update: dict | None = None
