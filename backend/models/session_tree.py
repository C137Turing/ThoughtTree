"""SessionTree ORM model — session_tree closure table."""
from sqlalchemy import Column, String, Integer, ForeignKey, PrimaryKeyConstraint

from db.base import Base


class SessionTree(Base):
    __tablename__ = "session_tree"

    ancestor_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    descendant_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    depth = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        PrimaryKeyConstraint("ancestor_id", "descendant_id"),
    )
