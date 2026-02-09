from __future__ import annotations

from pydantic import BaseModel, Field


class EmbedField(BaseModel):
    name: str
    value: str
    inline: bool = False


class NotifyRequest(BaseModel):
    title: str = "Notification"
    message: str
    color: int = 0x5865F2  # Discord blurple
    fields: list[EmbedField] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    wait: bool = False
    timeout: int = 300


class NotifyResponse(BaseModel):
    success: bool
    message_id: int | None = None
    response: str | None = None
    author: str | None = None
    timestamp: str | None = None
    error: str | None = None
