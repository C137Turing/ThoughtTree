"""Pydantic request/response schemas for the API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str = "new window"
    parent_id: Optional[str] = None
    root_id: Optional[str] = None


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    title: str
    parent_id: Optional[str] = None
    root_id: str
    status: str
    position_x: float = 0.0
    position_y: float = 0.0
    width: float = 600.0
    height: float = 400.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    is_quote: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    content: str


class UserConfigResponse(BaseModel):
    id: int = 1
    active_model: str = "deepseek-v4-flash"
    ears_enabled: bool = False
    numbering_style: str = "standard"
    sdd_mapping_rules: Optional[dict] = None

    model_config = {"from_attributes": True}


class UserConfigUpdate(BaseModel):
    active_model: Optional[str] = None
    ears_enabled: Optional[bool] = None
    numbering_style: Optional[str] = None
    sdd_mapping_rules: Optional[dict] = None
    api_key_encrypted: Optional[str] = None
