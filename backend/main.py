"""
BharatBridge — FastAPI Application Entry Point.
AI Execution Agent for public infrastructure — automates citizen access
to government welfare, scholarships, and subsidies.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.knowledge.graph import SchemeGraph
from backend.routers import citizens, schemes, applications, agents


# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bharatbridge")


# ── Lifespan (startup / shutdown) ────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scheme graph on startup."""
    logger.info("🚀 BharatBridge starting — building knowledge graph...")
    graph = SchemeGraph()
    stats = graph.stats()
    logger.info(
        f"✅ Knowledge graph ready: {stats['schemes']} schemes, "
        f"{stats['rules']} rules, {stats['documents']} doc types, "
        f"{stats['total_edges']} edges"
    )

    # Inject graph into routers
    schemes.init_graph(graph)
    agents.init_orchestrator(graph)

    yield

    logger.info("👋 BharatBridge shutting down")


# ── App ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BharatBridge",
    description=(
        "AI Execution Agent for Public Infrastructure — "
        "Multi-agent system automating citizen welfare benefit discovery, "
        "eligibility matching, document validation, adversarial analysis, "
        "and automated application submission."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(citizens.router)
app.include_router(schemes.router)
app.include_router(applications.router)
app.include_router(agents.router)


@app.get("/")
async def root():
    return {
        "name": "BharatBridge",
        "tagline": "AI Execution Agent for Public Infrastructure",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "citizens": "/api/citizens",
            "schemes": "/api/schemes",
            "applications": "/api/applications",
            "pipeline": "/api/agents/pipeline",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
