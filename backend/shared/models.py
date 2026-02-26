from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventStatus(str, Enum):
    OPEN = "open"
    AUTO_RESOLVED = "auto_resolved"
    ADVISER_RESOLVED = "adviser_resolved"
    DISMISSED = "dismissed"

class EventType(str, Enum):
    MARKET_RISK = "market_risk"
    TAX_OPPORTUNITY = "tax_opportunity"
    COMPLIANCE_EXPOSURE = "compliance_exposure"
    BEHAVIOURAL_RISK = "behavioural_risk"
    MARKET_INTERRUPT = "market_interrupt"
    MORNING_INTELLIGENCE = "morning_intelligence"

class Client(BaseModel):
    id: Optional[UUID] = None
    first_name: str
    last_name: str
    email: EmailStr
    tax_profile: Dict[str, Any] = Field(default_factory=dict)
    behavioural_profile: Dict[str, Any] = Field(default_factory=dict)
    vulnerability_score: float = 0.0
    vulnerability_category: Optional[str] = None
    vulnerability_notes: Optional[str] = None
    last_proactive_check: Optional[datetime] = None
    created_at: Optional[datetime] = None

class MarketSnapshot(BaseModel):
    id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ftse_100_value: float
    ftse_250_value: float
    sector_performance: Dict[str, float]
    raw_data: Optional[Dict[str, Any]] = None

class Portfolio(BaseModel):
    id: Optional[UUID] = None
    client_id: UUID
    holdings: List[Dict[str, Any]]
    total_value_gbp: float
    last_updated: datetime

class RiskEvent(BaseModel):
    id: Optional[UUID] = None
    client_id: UUID
    event_type: EventType
    urgency: UrgencyLevel
    deterministic_classification: Dict[str, Any]
    ai_interpretation: Optional[Dict[str, Any]] = None
    status: EventStatus = EventStatus.OPEN
    model_version: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class BehaviouralMemory(BaseModel):
    id: Optional[UUID] = None
    client_id: UUID
    content: str
    source_reference: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MeetingBrief(BaseModel):
    id: Optional[UUID] = None
    client_id: UUID
    meeting_timestamp: datetime
    brief_json: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DraftAction(BaseModel):
    id: Optional[UUID] = None
    risk_event_id: UUID
    client_id: UUID
    action_type: str
    draft_content: Dict[str, Any]
    compliance_check_status: str = "pending"
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HeartbeatLog(BaseModel):
    id: Optional[UUID] = None
    sweep_type: str  # "book_sweep", "mandate_check", "feed_sync"
    portfolios_scanned: int = 0
    risks_found: int = 0
    result_summary: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
