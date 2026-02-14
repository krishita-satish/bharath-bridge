"""Application lifecycle and tracking data models."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    READY = "ready"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPEALED = "appealed"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_REJECTED = "appeal_rejected"


class AuditEntry(BaseModel):
    """Audit log entry for submission attempts (Req 5.7)."""

    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    action: str = ""
    agent: str = ""
    details: str = ""
    portal_url: str = ""
    response_code: Optional[int] = None
    error_message: str = ""
    success: bool = False


class RejectionAnalysis(BaseModel):
    """Adversarial validation result (Req 4)."""

    rejection_probability: float = 0.0  # 0.0–1.0 (displayed as 0–100%)
    risk_level: str = "low"  # low / medium / high / critical
    risk_factors: list[dict] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    common_rejection_patterns: list[str] = Field(default_factory=list)


class Application(BaseModel):
    """Full application lifecycle — maps to DynamoDB Applications table."""

    application_id: str = Field(default="")
    citizen_id: str = ""
    scheme_id: str = ""
    scheme_name: str = ""
    status: ApplicationStatus = ApplicationStatus.DRAFT

    # Submission
    submission_date: Optional[str] = None
    confirmation_number: str = ""
    portal_url: str = ""
    execution_tier: int = 2  # 1/2/3
    documents_submitted: list[str] = Field(default_factory=list)

    # Rejection analysis (from Adversarial Agent)
    rejection_analysis: Optional[RejectionAnalysis] = None

    # Rejection info (if rejected)
    rejection_reason: str = ""
    rejection_date: Optional[str] = None

    # Appeal
    appeal_letter: str = ""
    appeal_status: str = ""
    appeal_date: Optional[str] = None

    # Tracking
    expected_decision_date: Optional[str] = None
    benefit_amount: float = 0.0
    disbursement_details: str = ""

    # Audit
    audit_trail: list[AuditEntry] = Field(default_factory=list)

    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def add_audit(self, action: str, agent: str, details: str = "",
                  success: bool = True, error: str = "") -> None:
        self.audit_trail.append(AuditEntry(
            action=action,
            agent=agent,
            details=details,
            success=success,
            error_message=error,
        ))
        self.updated_at = datetime.now().isoformat()
