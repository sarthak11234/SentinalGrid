"""
ORM models for Campaign and DataRow.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    master_prompt = Column(Text, nullable=False)
    status = Column(String, default="draft")  # draft | running | completed | failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    rows = relationship("DataRow", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Campaign {self.id}: {self.name}>"


class DataRow(Base):
    __tablename__ = "data_rows"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    row_index = Column(Integer, nullable=False)

    # Original row data stored as JSON
    row_data = Column(JSON, nullable=False)

    # Contact info extracted from the row
    contact_email = Column(String, nullable=True, index=True)
    contact_phone = Column(String, nullable=True, index=True)
    channel = Column(String, default="email")  # email | whatsapp

    # Messaging state
    message_status = Column(String, default="pending")  # pending | sent | replied | review | failed
    outbound_message = Column(Text, nullable=True)

    # Reply processing
    reply_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    needs_review = Column(Boolean, default=False)
    suggested_update = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    campaign = relationship("Campaign", back_populates="rows")

    def __repr__(self):
        return f"<DataRow {self.id} (campaign={self.campaign_id}, row={self.row_index})>"
