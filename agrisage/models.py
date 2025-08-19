from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class Context(BaseModel):
    location: Optional[str] = None
    district: Optional[str] = None
    crop: Optional[str] = None
    stage: Optional[str] = None
    profile: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"land_owner": True, "cultivator": True, "notified_district": True}
    )
    soil_card: Optional[Dict[str, Any]] = None

class AskRequest(BaseModel):
    query: str
    context: Optional[Context] = None

class AskResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    explain: Dict[str, Any]
    warnings: List[str]
    meta: Dict[str, Any]

class IngestDoc(BaseModel):
    id: str
    text: str
    meta: Dict[str, Any] = {}

