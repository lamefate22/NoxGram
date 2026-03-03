from pydantic import BaseModel, Field
from typing import Dict


class SessionModel(BaseModel):
    __slots__ = ("salt", "api_id", "api_hash", "session_string")

    salt: str
    api_id: int
    api_hash: str
    session_string: str


class SettingsModel(BaseModel):
    sessions: Dict[str, SessionModel] = Field(default_factory=dict)
