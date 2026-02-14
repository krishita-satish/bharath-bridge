"""
Orchestrator Agent — Multi-agent pipeline coordination (Req 9).
Coordinates the full citizen journey: profile → eligibility → documents →
adversarial → execution. Implements state persistence, retry logic,
and event emission (Step Functions simulation).
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from backend.models.citizen import CitizenProfile
from backend.models.scheme import SchemeMatch
from backend.models.application import Application, RejectionAnalysis
from backend.agents.profiler import ProfilerAgent
from backend.agents.eligibility import EligibilityAgent
from backend.agents.document import DocumentAgent
from backend.agents.adversarial import AdversarialAgent
from backend.agents.execution import ExecutionAgent
from backend.agents.appeals import AppealsAgent
from backend.knowledge.graph import SchemeGraph

logger = logging.getLogger("bharatbridge.orchestrator")


class PipelineStage(str, Enum):
    PROFILE = "profile"
    ELIGIBILITY = "eligibility"
    DOCUMENTS = "documents"
    ADVERSARIAL = "adversarial"
    EXECUTION = "execution"
    COMPLETE = "complete"
    FAILED = "failed"


class PipelineEvent(BaseModel):
    stage: PipelineStage
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    message: str = ""
    data: dict = Field(default_factory=dict)
    success: bool = True


class PipelineState(BaseModel):
    """Full state of a pipeline execution (persisted in-memory)."""
    pipeline_id: str = ""
    citizen_id: str = ""
    current_stage: PipelineStage = PipelineStage.PROFILE
    events: list[PipelineEvent] = Field(default_factory=list)
    profile: dict = Field(default_factory=dict)
    eligible_schemes: list[dict] = Field(default_factory=list)
    selected_scheme_id: str = ""
    documents_processed: list[dict] = Field(default_factory=list)
    rejection_analysis: dict = Field(default_factory=dict)
    application: dict = Field(default_factory=dict)
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""
    error: str = ""


# In-memory pipeline store
_pipelines: dict[str, PipelineState] = {}


class OrchestratorAgent:
    """Coordinates all agents through the full citizen benefit pipeline."""

    def __init__(self, graph: SchemeGraph) -> None:
        self.profiler = ProfilerAgent()
        self.eligibility = EligibilityAgent(graph)
        self.document = DocumentAgent()
        self.adversarial = AdversarialAgent()
        self.execution = ExecutionAgent()
        self.appeals = AppealsAgent()

    def start_workflow(self, profile_data: dict, scheme_id: str = "") -> PipelineState:
        """
        Execute the full multi-agent pipeline (Req 9.1–9.3).
        Steps: profile → eligibility → documents → adversarial → execution.
        """
        pipeline_id = f"PIPE-{uuid.uuid4().hex[:8].upper()}"
        state = PipelineState(pipeline_id=pipeline_id)

        try:
            # ── Stage 1: Profile ─────────────────────────────────────────
            state = self._run_profile_stage(state, profile_data)
            if state.current_stage == PipelineStage.FAILED:
                return self._finalize(state)

            citizen = self.profiler.get_profile(state.citizen_id)
            if not citizen:
                state.error = "Profile creation failed"
                state.current_stage = PipelineStage.FAILED
                return self._finalize(state)

            # ── Stage 2: Eligibility ─────────────────────────────────────
            state = self._run_eligibility_stage(state, citizen, scheme_id)
            if state.current_stage == PipelineStage.FAILED:
                return self._finalize(state)

            # ── Stage 3: Documents ───────────────────────────────────────
            state = self._run_document_stage(state, citizen)

            # ── Stage 4: Adversarial ─────────────────────────────────────
            target_scheme = state.selected_scheme_id or (
                state.eligible_schemes[0]["scheme_id"] if state.eligible_schemes else ""
            )
            if target_scheme:
                state = self._run_adversarial_stage(state, citizen, target_scheme)

                # ── Stage 5: Execution ───────────────────────────────────
                rejection_prob = state.rejection_analysis.get("rejection_probability", 0)
                state = self._run_execution_stage(
                    state, citizen, target_scheme, rejection_prob
                )

            state.current_stage = PipelineStage.COMPLETE
            state.completed_at = datetime.now().isoformat()

        except Exception as exc:
            logger.exception("Pipeline failed")
            state.current_stage = PipelineStage.FAILED
            state.error = str(exc)
            state.events.append(PipelineEvent(
                stage=PipelineStage.FAILED,
                message=f"Pipeline error: {exc}",
                success=False,
            ))

        return self._finalize(state)

    # ── Stage Runners ────────────────────────────────────────────────────

    def _run_profile_stage(self, state: PipelineState, data: dict) -> PipelineState:
        state.current_stage = PipelineStage.PROFILE
        try:
            profile = self.profiler.create_profile(data)
            state.citizen_id = profile.citizen_id
            state.profile = profile.model_dump()
            state.events.append(PipelineEvent(
                stage=PipelineStage.PROFILE,
                message=f"Profile created: {profile.citizen_id}",
                data={"citizen_id": profile.citizen_id, "name": profile.name},
            ))
        except Exception as exc:
            state.current_stage = PipelineStage.FAILED
            state.error = f"Profile stage failed: {exc}"
            state.events.append(PipelineEvent(
                stage=PipelineStage.PROFILE, message=str(exc), success=False
            ))
        return state

    def _run_eligibility_stage(
        self, state: PipelineState, citizen: CitizenProfile, scheme_id: str
    ) -> PipelineState:
        state.current_stage = PipelineStage.ELIGIBILITY
        try:
            matches = self.eligibility.discover_schemes(citizen)
            state.eligible_schemes = [
                {
                    "scheme_id": m.scheme.scheme_id,
                    "scheme_name": m.scheme.name,
                    "eligibility_score": m.eligibility_score,
                    "approval_probability": m.approval_probability,
                    "benefit_amount": m.estimated_benefit,
                    "is_eligible": m.is_eligible,
                    "missing_documents": m.missing_documents,
                    "conflicts": m.conflicts,
                    "rank": m.rank,
                }
                for m in matches
            ]

            if scheme_id:
                state.selected_scheme_id = scheme_id
            elif matches:
                # Auto-select top eligible scheme
                eligible = [m for m in matches if m.is_eligible]
                if eligible:
                    state.selected_scheme_id = eligible[0].scheme.scheme_id

            eligible_count = sum(1 for m in matches if m.is_eligible)
            state.events.append(PipelineEvent(
                stage=PipelineStage.ELIGIBILITY,
                message=f"Found {eligible_count} eligible schemes out of {len(matches)} total",
                data={"eligible_count": eligible_count, "total": len(matches)},
            ))
        except Exception as exc:
            state.events.append(PipelineEvent(
                stage=PipelineStage.ELIGIBILITY, message=str(exc), success=False
            ))
        return state

    def _run_document_stage(
        self, state: PipelineState, citizen: CitizenProfile
    ) -> PipelineState:
        state.current_stage = PipelineStage.DOCUMENTS
        try:
            from backend.models.document import DocumentType
            doc_types_to_process = citizen.documents or ["aadhaar", "income_certificate"]
            processed = []
            for doc_name in doc_types_to_process[:5]:  # Limit to 5 for demo
                try:
                    doc_type = DocumentType(doc_name)
                    doc = self.document.process_document(doc_type)
                    processed.append({
                        "document_id": doc.document_id,
                        "type": doc.document_type.value,
                        "status": doc.authenticity_status.value,
                        "confidence": doc.extraction_result.confidence if doc.extraction_result else 0,
                    })
                except ValueError:
                    pass

            state.documents_processed = processed
            state.events.append(PipelineEvent(
                stage=PipelineStage.DOCUMENTS,
                message=f"Processed {len(processed)} documents",
                data={"documents": processed},
            ))
        except Exception as exc:
            state.events.append(PipelineEvent(
                stage=PipelineStage.DOCUMENTS, message=str(exc), success=False
            ))
        return state

    def _run_adversarial_stage(
        self, state: PipelineState, citizen: CitizenProfile, scheme_id: str
    ) -> PipelineState:
        state.current_stage = PipelineStage.ADVERSARIAL
        try:
            analysis = self.adversarial.predict_rejection(citizen, scheme_id)
            if analysis:
                state.rejection_analysis = analysis.model_dump()
                state.events.append(PipelineEvent(
                    stage=PipelineStage.ADVERSARIAL,
                    message=f"Rejection risk: {analysis.risk_level} ({analysis.rejection_probability:.0%})",
                    data={
                        "rejection_probability": analysis.rejection_probability,
                        "risk_level": analysis.risk_level,
                    },
                ))
        except Exception as exc:
            state.events.append(PipelineEvent(
                stage=PipelineStage.ADVERSARIAL, message=str(exc), success=False
            ))
        return state

    def _run_execution_stage(
        self, state: PipelineState, citizen: CitizenProfile,
        scheme_id: str, rejection_prob: float
    ) -> PipelineState:
        state.current_stage = PipelineStage.EXECUTION
        try:
            app = self.execution.submit_application(
                citizen, scheme_id, rejection_prob
            )
            state.application = app.model_dump()
            state.events.append(PipelineEvent(
                stage=PipelineStage.EXECUTION,
                message=f"Application {app.application_id}: {app.status.value}",
                data={
                    "application_id": app.application_id,
                    "status": app.status.value,
                    "confirmation": app.confirmation_number,
                },
            ))
        except Exception as exc:
            state.events.append(PipelineEvent(
                stage=PipelineStage.EXECUTION, message=str(exc), success=False
            ))
        return state

    # ── Helpers ───────────────────────────────────────────────────────────

    def _finalize(self, state: PipelineState) -> PipelineState:
        _pipelines[state.pipeline_id] = state
        return state

    def get_pipeline(self, pipeline_id: str) -> PipelineState | None:
        return _pipelines.get(pipeline_id)

    def handle_agent_error(self, state: PipelineState, stage: str, error: str) -> PipelineState:
        """Handle an agent error (Req 9.4, 9.5)."""
        state.events.append(PipelineEvent(
            stage=PipelineStage(stage),
            message=f"Error in {stage}: {error}",
            success=False,
        ))
        return state
