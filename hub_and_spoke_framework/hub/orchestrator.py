from typing import List
from common.models import Transaction, OrchestrationResponse, Finding, SpokeCapability
from hub.registry import AgentRegistry
from hub.observability import AuditStore
import uuid

class Orchestrator:
    def __init__(self, registry: AgentRegistry, audit_store: AuditStore):
        self.registry = registry
        self.audit_store = audit_store

    def process_request(self, transaction: Transaction) -> str:
        request_id = str(uuid.uuid4())
        self.audit_store.log_event("REQUEST_RECEIVED", {"request_id": request_id, "transaction": transaction.dict()})
        self.audit_store.log_event("ORCHESTRATION_STARTED", {"request_id": request_id})
        return request_id

    def execute_spokes(self, request_id: str, transaction: Transaction, spokes: List[Any]) -> List[Finding]:
        findings: List[Finding] = []
        for spoke in spokes:
            self.audit_store.log_event("SPOKE_INVOKED", {"request_id": request_id, "spoke_name": spoke.name})
            finding = spoke.process_transaction(transaction)
            findings.append(finding)
            self.audit_store.log_event("SPOKE_RESPONSE_RECEIVED", {"request_id": request_id, "spoke_name": spoke.name, "finding": finding.dict()})
        return findings

    def aggregate_results(self, request_id: str, findings: List[Finding]) -> OrchestrationResponse:
        # Compute consensus (simple mean for demo)
        if not findings:
            score = 0.0
            decision = "APPROVED"
        else:
            score = sum(f.score for f in findings) / len(findings)
            decision = "FLAGGED" if score > 0.5 else "APPROVED"

        response = OrchestrationResponse(
            request_id=request_id,
            findings=findings,
            consensus_score=score,
            final_decision=decision,
            audit_trail_id=request_id
        )

        self.audit_store.log_event("REQUEST_COMPLETED", response.dict())
        return response
