"""
Eligibility Agent — Scheme discovery and matching via graph reasoning (Req 2).
Uses the SchemeGraph to find eligible schemes, rank them, detect conflicts,
and discover benefit chains.
"""

from __future__ import annotations

from backend.models.citizen import CitizenProfile
from backend.models.scheme import SchemeMatch
from backend.knowledge.graph import SchemeGraph
from backend.knowledge.schemes_data import SCHEME_MAP


class EligibilityAgent:
    """Discovers eligible schemes for a citizen using graph-based reasoning."""

    def __init__(self, graph: SchemeGraph) -> None:
        self.graph = graph

    def discover_schemes(self, citizen: CitizenProfile) -> list[SchemeMatch]:
        """
        Find all schemes the citizen qualifies for (Req 2.1).
        Returns ranked list sorted by benefit × approval probability.
        """
        return self.graph.discover_schemes(citizen)

    def verify_eligibility(
        self, citizen: CitizenProfile, scheme_id: str
    ) -> SchemeMatch | None:
        """
        Verify a citizen's eligibility for a specific scheme (Req 2.2).
        Returns the match result or None if scheme not found.
        """
        scheme = SCHEME_MAP.get(scheme_id)
        if not scheme:
            return None

        matches = self.graph.discover_schemes(citizen)
        for match in matches:
            if match.scheme.scheme_id == scheme_id:
                return match
        return None

    def find_benefit_chains(self, scheme_id: str) -> list[str]:
        """
        Find schemes unlocked by this scheme (multi-hop, Req 2.5).
        """
        dependent_ids = self.graph.find_benefit_chain(scheme_id)
        return [
            SCHEME_MAP[sid].name
            for sid in dependent_ids
            if sid in SCHEME_MAP
        ]

    def detect_conflicts(self, scheme_ids: list[str]) -> list[dict]:
        """
        Detect mutually exclusive schemes (Req 2.4, Property 7).
        """
        conflict_pairs = self.graph.detect_conflicts(scheme_ids)
        results = []
        for a, b in conflict_pairs:
            name_a = SCHEME_MAP[a].name if a in SCHEME_MAP else a
            name_b = SCHEME_MAP[b].name if b in SCHEME_MAP else b
            results.append({
                "scheme_a": a,
                "scheme_a_name": name_a,
                "scheme_b": b,
                "scheme_b_name": name_b,
                "message": f"'{name_a}' and '{name_b}' are mutually exclusive. Apply for only one.",
            })
        return results

    def get_top_schemes(
        self, citizen: CitizenProfile, limit: int = 5
    ) -> list[SchemeMatch]:
        """Return top N eligible schemes by benefit ranking."""
        matches = self.discover_schemes(citizen)
        eligible = [m for m in matches if m.is_eligible]
        return eligible[:limit]
