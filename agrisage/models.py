
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class Context(BaseModel):
    location: Optional[str] = "Sikar, Rajasthan"
    district: Optional[str] = "Sikar"
    crop: Optional[str] = "wheat"
    stage: Optional[str] = "vegetative"
    profile: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"land_owner": True, "cultivator": True, "notified_district": True})
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
