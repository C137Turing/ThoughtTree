"""UserConfig ORM model — user_config table (single-row)."""
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Boolean,
    DateTime,
    Enum,
    JSON,
)

from db.base import Base


class UserConfig(Base):
    __tablename__ = "user_config"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, default=1)
    api_key_encrypted = Column(Text, nullable=True)
    active_model = Column(String(50), default="deepseek-v4-flash")
    ears_enabled = Column(Boolean, default=False)
    numbering_style = Column(
        Enum("standard", "chinese", name="numbering_style"),
        default="standard",
    )
    sdd_mapping_rules = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
