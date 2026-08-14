"""Message ORM model — messages table."""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
)

from db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(
        Enum("user", "assistant", "system", name="message_role"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    is_quote = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
