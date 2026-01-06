from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class AgentRole(str, Enum):
    HUB = "hub"
    SPOKE = "spoke"

class SpokeCapability(str, Enum):
    AML = "aml"
    FRAUD = "fraud"
    CREDIT = "credit"
    COMPLIANCE = "compliance"

class Transaction(BaseModel):
    transaction_id: str
    amount: float
    currency: str = "USD"
    sender_id: str
    receiver_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class Finding(BaseModel):
    spoke_name: str
    severity: str  # e.g., "LOW", "MEDIUM", "HIGH", "CRITICAL"
    score: float   # 0.0 to 1.0
    rationale: str
    action_item: Optional[str] = None

class OrchestrationResponse(BaseModel):
    request_id: str
    findings: List[Finding]
    consensus_score: float
    final_decision: str
    audit_trail_id: str
