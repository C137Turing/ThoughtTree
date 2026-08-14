"""Session ORM model — sessions table."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from db.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    parent_id = Column(String(36), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    root_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        Enum("open", "closed", "minimized", name="session_status"),
        default="open",
        nullable=False,
    )
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    width = Column(Float, default=600.0)
    height = Column(Float, default=400.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Session", remote_side=[id], backref="children")
    root = relationship("Session", remote_side=[id], foreign_keys=[root_id])
