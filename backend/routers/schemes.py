"""Scheme discovery and eligibility routes (Req 2, 8)."""

from fastapi import APIRouter, HTTPException

from backend.models.citizen import CitizenProfile
from backend.agents.eligibility import EligibilityAgent
from backend.knowledge.graph import SchemeGraph
from backend.knowledge.schemes_data import SCHEMES, SCHEME_MAP

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])

# Graph will be initialized in main.py startup and injected
_graph: SchemeGraph | None = None
_eligibility: EligibilityAgent | None = None


def init_graph(graph: SchemeGraph):
    global _graph, _eligibility
    _graph = graph
    _eligibility = EligibilityAgent(graph)


@router.get("/")
async def list_schemes():
    """List all available welfare schemes (Req 8)."""
    return {
        "schemes": [s.model_dump() for s in SCHEMES],
        "count": len(SCHEMES),
    }


@router.get("/{scheme_id}")
async def get_scheme(scheme_id: str):
    """Get a specific scheme by ID."""
    scheme = SCHEME_MAP.get(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {"scheme": scheme.model_dump()}


@router.post("/discover")
async def discover_schemes(profile: dict):
    """
    Discover eligible schemes for a citizen profile (Req 2.1).
    Accepts a citizen profile dict and returns ranked matches.
    """
    if not _eligibility:
        raise HTTPException(status_code=503, detail="Scheme graph not initialized")

    try:
        citizen = CitizenProfile(**profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid profile: {e}")

    matches = _eligibility.discover_schemes(citizen)

    return {
        "matches": [m.model_dump() for m in matches],
        "eligible_count": sum(1 for m in matches if m.is_eligible),
        "total_schemes": len(matches),
    }


@router.post("/conflicts")
async def check_conflicts(data: dict):
    """Check for conflicts between selected schemes (Req 2.4)."""
    if not _eligibility:
        raise HTTPException(status_code=503, detail="Scheme graph not initialized")

    scheme_ids = data.get("scheme_ids", [])
    conflicts = _eligibility.detect_conflicts(scheme_ids)
    return {"conflicts": conflicts, "has_conflicts": len(conflicts) > 0}


@router.get("/graph/stats")
async def graph_stats():
    """Get knowledge graph statistics."""
    if not _graph:
        raise HTTPException(status_code=503, detail="Graph not initialized")
    return _graph.stats()
