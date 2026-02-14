"""
Full multi-agent pipeline route (Req 9).
Single endpoint to execute the entire citizen benefit journey.
"""

from fastapi import APIRouter, HTTPException

from backend.agents.orchestrator import OrchestratorAgent
from backend.knowledge.graph import SchemeGraph

router = APIRouter(prefix="/api/agents", tags=["Agents"])

_orchestrator: OrchestratorAgent | None = None


def init_orchestrator(graph: SchemeGraph):
    global _orchestrator
    _orchestrator = OrchestratorAgent(graph)


@router.post("/pipeline")
async def run_pipeline(data: dict):
    """
    Run the full multi-agent pipeline (Req 9.1).
    Expects a citizen profile dict and optionally a scheme_id.
    Returns the full pipeline state including all agent results.
    """
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    profile_data = data.get("profile", data)
    scheme_id = data.get("scheme_id", "")

    state = _orchestrator.start_workflow(profile_data, scheme_id)

    return {
        "pipeline_id": state.pipeline_id,
        "status": state.current_stage.value,
        "citizen_id": state.citizen_id,
        "eligible_schemes": state.eligible_schemes,
        "selected_scheme": state.selected_scheme_id,
        "documents_processed": state.documents_processed,
        "rejection_analysis": state.rejection_analysis,
        "application": state.application,
        "events": [e.model_dump() for e in state.events],
        "error": state.error,
    }


@router.get("/pipeline/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    """Get pipeline execution status."""
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    state = _orchestrator.get_pipeline(pipeline_id)
    if not state:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return {
        "pipeline_id": state.pipeline_id,
        "status": state.current_stage.value,
        "events": [e.model_dump() for e in state.events],
        "application": state.application,
    }
