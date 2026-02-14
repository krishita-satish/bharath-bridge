"""Application submission, tracking, and appeals routes (Req 5, 6, 7)."""

from fastapi import APIRouter, HTTPException

from backend.models.citizen import CitizenProfile
from backend.agents.profiler import ProfilerAgent
from backend.agents.execution import ExecutionAgent
from backend.agents.adversarial import AdversarialAgent
from backend.agents.appeals import AppealsAgent

router = APIRouter(prefix="/api/applications", tags=["Applications"])

_profiler = ProfilerAgent()
_execution = ExecutionAgent()
_adversarial = AdversarialAgent()
_appeals = AppealsAgent()


@router.post("/submit")
async def submit_application(data: dict):
    """
    Submit an application for a scheme (Req 5.1).
    Requires citizen_id and scheme_id in the body.
    """
    citizen_id = data.get("citizen_id")
    scheme_id = data.get("scheme_id")

    if not citizen_id or not scheme_id:
        raise HTTPException(status_code=400, detail="citizen_id and scheme_id required")

    citizen = _profiler.get_profile(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    try:
        app = _execution.submit_application(citizen, scheme_id)
        return {
            "status": "submitted",
            "application": app.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{application_id}")
async def get_application_status(application_id: str):
    """Get application status with simulated progression (Req 6.1)."""
    app = _execution.poll_status(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"application": app.model_dump()}


@router.get("/citizen/{citizen_id}")
async def list_citizen_applications(citizen_id: str):
    """List all applications for a citizen (Req 6.7)."""
    apps = _execution.list_applications(citizen_id)
    return {
        "applications": [a.model_dump() for a in apps],
        "count": len(apps),
    }


@router.post("/{application_id}/predict")
async def predict_rejection(application_id: str, data: dict):
    """
    Run adversarial analysis on a pending application (Req 4).
    """
    citizen_id = data.get("citizen_id")
    if not citizen_id:
        raise HTTPException(status_code=400, detail="citizen_id required")

    citizen = _profiler.get_profile(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    app = _execution.get_application(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    analysis = _adversarial.predict_rejection(citizen, app.scheme_id)
    if not analysis:
        raise HTTPException(status_code=400, detail="Could not predict rejection")

    return {"analysis": analysis.model_dump()}


@router.post("/{application_id}/appeal")
async def generate_appeal(application_id: str, data: dict):
    """
    Generate and submit an appeal for a rejected application (Req 7).
    """
    app = _execution.get_application(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app.status.value != "rejected":
        raise HTTPException(status_code=400, detail="Can only appeal rejected applications")

    citizen_id = data.get("citizen_id")
    citizen = _profiler.get_profile(citizen_id) if citizen_id else None
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    language = data.get("language", "english")

    # Analyze rejection
    analysis = _appeals.analyze_rejection(app)

    # Generate letter
    letter = _appeals.generate_appeal_letter(app, citizen, language)

    # Submit appeal
    app = _appeals.submit_appeal(app, letter["letter_text"])

    return {
        "analysis": analysis,
        "letter": letter,
        "application": app.model_dump(),
    }
