# home_assistant_schema.py

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class HomeAssistantCommand(BaseModel):
    """Schema for structured Home Assistant command output from the LLM."""
    action: str
    devices: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
