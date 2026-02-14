"""
Execution Agent — 3-tier application submission and tracking (Req 5, 6).
Simulates API submission, web automation, and PDF fallback with retry,
confirmation capture, and audit logging.
"""

from __future__ import annotations

import uuid
import random
import asyncio
from datetime import datetime, timedelta

from backend.models.application import Application, ApplicationStatus, AuditEntry
from backend.models.citizen import CitizenProfile
from backend.models.scheme import Scheme
from backend.knowledge.schemes_data import SCHEME_MAP


# In-memory application store
_applications: dict[str, Application] = {}

# Retry configuration (Req 5.5)
MAX_RETRIES = 3
BACKOFF_BASE = 1  # seconds


class ExecutionAgent:
    """Handles multi-tier application submission and tracking."""

    def submit_application(
        self,
        citizen: CitizenProfile,
        scheme_id: str,
        rejection_probability: float = 0.0,
    ) -> Application:
        """
        Submit an application using the appropriate tier (Req 5.1–5.3).
        Tier 1: API → Tier 2: Web Automation → Tier 3: PDF Generation.
        """
        scheme = SCHEME_MAP.get(scheme_id)
        if not scheme:
            raise ValueError(f"Scheme '{scheme_id}' not found")

        app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"

        app = Application(
            application_id=app_id,
            citizen_id=citizen.citizen_id,
            scheme_id=scheme_id,
            scheme_name=scheme.name,
            status=ApplicationStatus.DRAFT,
            execution_tier=scheme.execution_tier,
            portal_url=scheme.portal_url,
            benefit_amount=scheme.benefit_amount,
            expected_decision_date=(
                datetime.now() + timedelta(days=scheme.processing_days)
            ).isoformat(),
        )

        # Simulate tier-based submission
        success = False
        tier = scheme.execution_tier

        for attempt in range(1, MAX_RETRIES + 1):
            result = self._execute_tier(tier, citizen, scheme, attempt)
            app.add_audit(
                action=f"Tier {tier} submission attempt {attempt}",
                agent="ExecutionAgent",
                details=result["message"],
                success=result["success"],
                error=result.get("error", ""),
            )

            if result["success"]:
                success = True
                app.confirmation_number = result.get("confirmation", "")
                break

            # Fallback to next tier
            if attempt == MAX_RETRIES and tier < 3:
                tier += 1
                app.execution_tier = tier
                app.add_audit(
                    action=f"Tier fallback to Tier {tier}",
                    agent="ExecutionAgent",
                    details=f"Falling back from Tier {tier-1} to Tier {tier}",
                    success=True,
                )

        if success:
            app.status = ApplicationStatus.SUBMITTED
            app.submission_date = datetime.now().isoformat()
        else:
            app.status = ApplicationStatus.DRAFT
            app.add_audit(
                action="Submission failed",
                agent="ExecutionAgent",
                details="All tiers exhausted. Application saved as draft for manual submission.",
                success=False,
            )

        _applications[app_id] = app
        return app

    def _execute_tier(
        self, tier: int, citizen: CitizenProfile, scheme: Scheme, attempt: int
    ) -> dict:
        """Simulate a tier execution attempt."""
        # Simulated success probability (higher for lower tiers)
        success_rate = {1: 0.90, 2: 0.80, 3: 0.95}
        prob = success_rate.get(tier, 0.80)

        success = random.random() < prob

        if tier == 1:
            action = "API submission to portal"
        elif tier == 2:
            action = "Web automation form-fill"
        else:
            action = "PDF generation and upload"

        if success:
            conf = f"CONF-{uuid.uuid4().hex[:10].upper()}"
            return {
                "success": True,
                "message": f"{action} succeeded on attempt {attempt}",
                "confirmation": conf,
            }
        else:
            return {
                "success": False,
                "message": f"{action} failed on attempt {attempt}",
                "error": "Simulated transient failure — portal timeout",
            }

    def poll_status(self, application_id: str) -> Application | None:
        """
        Poll application status (Req 6.1, 6.2).
        Simulates status progression over time.
        """
        app = _applications.get(application_id)
        if not app:
            return None

        # Simulate status progression
        if app.status == ApplicationStatus.SUBMITTED:
            # Randomly progress to next stage
            roll = random.random()
            if roll < 0.3:
                app.status = ApplicationStatus.UNDER_REVIEW
                app.add_audit(
                    action="Status update",
                    agent="ExecutionAgent",
                    details="Application moved to under review by department",
                    success=True,
                )
            _applications[app.application_id] = app

        elif app.status == ApplicationStatus.UNDER_REVIEW:
            roll = random.random()
            if roll < 0.2:
                app.status = ApplicationStatus.APPROVED
                app.disbursement_details = "Benefit will be credited to linked bank account via DBT"
                app.add_audit(
                    action="Application approved",
                    agent="ExecutionAgent",
                    details="Application approved by competent authority",
                    success=True,
                )
            elif roll < 0.3:
                app.status = ApplicationStatus.REJECTED
                app.rejection_reason = "Document verification discrepancy found"
                app.rejection_date = datetime.now().isoformat()
                app.add_audit(
                    action="Application rejected",
                    agent="ExecutionAgent",
                    details=f"Rejected: {app.rejection_reason}",
                    success=False,
                )
            _applications[app.application_id] = app

        return app

    def generate_prefilled_pdf(
        self, citizen: CitizenProfile, scheme_id: str
    ) -> dict:
        """
        Generate a pre-filled PDF form for manual submission (Req 5.3).
        Returns metadata about the generated PDF.
        """
        scheme = SCHEME_MAP.get(scheme_id)
        if not scheme:
            return {"error": "Scheme not found"}

        return {
            "pdf_id": f"PDF-{uuid.uuid4().hex[:8].upper()}",
            "scheme_name": scheme.name,
            "citizen_name": citizen.name,
            "status": "generated",
            "fields_filled": {
                "full_name": citizen.name,
                "date_of_birth": citizen.date_of_birth,
                "aadhaar_number": "XXXX-XXXX-" + citizen.aadhaar_number[-4:] if len(citizen.aadhaar_number) >= 4 else "",
                "address": f"{citizen.address.line1}, {citizen.address.city}, {citizen.address.state} - {citizen.address.pincode}",
                "annual_income": str(citizen.annual_income),
                "bank_account": "XXXX" + citizen.bank_account[-4:] if len(citizen.bank_account) >= 4 else "",
                "category": citizen.caste_category.value.upper(),
            },
            "portal_url": scheme.portal_url,
            "instructions": "Print this form, sign it, and submit at your nearest CSC or district office.",
        }

    def get_application(self, application_id: str) -> Application | None:
        """Get application by ID."""
        return _applications.get(application_id)

    def list_applications(self, citizen_id: str) -> list[Application]:
        """List all applications for a citizen (Req 6.7)."""
        return [
            app for app in _applications.values()
            if app.citizen_id == citizen_id
        ]
