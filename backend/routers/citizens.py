"""Citizen profile management routes (Req 1)."""

from fastapi import APIRouter, HTTPException

from backend.agents.profiler import ProfilerAgent

router = APIRouter(prefix="/api/citizens", tags=["Citizens"])
_profiler = ProfilerAgent()


@router.post("/profile")
async def create_profile(data: dict):
    """Create or update a citizen profile (Req 1.1, 1.2)."""
    citizen_id = data.get("citizen_id")
    if citizen_id:
        existing = _profiler.get_profile(citizen_id)
        if existing:
            updated = _profiler.update_profile(citizen_id, data)
            return {"status": "updated", "profile": updated.model_dump()}

    profile = _profiler.create_profile(data)
    return {"status": "created", "profile": profile.model_dump()}


@router.get("/profiles")
async def list_profiles():
    """List all citizen profiles."""
    profiles = _profiler.list_profiles()
    return {"profiles": [p.model_dump() for p in profiles], "count": len(profiles)}


@router.get("/{citizen_id}")
async def get_profile(citizen_id: str):
    """Get a citizen profile by ID."""
    profile = _profiler.get_profile(citizen_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Citizen not found")
    return {"profile": profile.model_dump()}


@router.delete("/{citizen_id}")
async def delete_profile(citizen_id: str):
    """Delete citizen data (GDPR compliance, Req 1.7, 10.4)."""
    deleted = _profiler.delete_profile(citizen_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Citizen not found")
    return {"status": "deleted", "citizen_id": citizen_id}
