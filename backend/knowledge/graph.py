"""
NetworkX-based knowledge graph simulating Amazon Neptune.
Builds a scheme–rule–document graph and supports multi-hop traversals,
conflict detection, and benefit-chain discovery (Req 2, 8).
"""

from __future__ import annotations

import networkx as nx
from typing import Optional

from backend.models.citizen import CitizenProfile, EducationLevel
from backend.models.scheme import Scheme, EligibilityRule, RuleType, SchemeMatch
from backend.knowledge.schemes_data import SCHEMES, SCHEME_MAP


# Education level ordering for comparisons
_EDU_ORDER: dict[str, int] = {
    "none": 0,
    "primary": 1,
    "secondary": 2,
    "higher_secondary": 3,
    "graduate": 4,
    "post_graduate": 5,
    "doctorate": 6,
}

MAX_HOPS = 5  # Req 2.5: multi-hop traversal limit


class SchemeGraph:
    """Scheme knowledge graph — Neptune simulation using NetworkX."""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self._build()

    # ── Graph Construction ───────────────────────────────────────────────

    def _build(self) -> None:
        """Build the full graph from scheme data."""
        for scheme in SCHEMES:
            # Scheme node
            self.graph.add_node(
                scheme.scheme_id,
                node_type="scheme",
                name=scheme.name,
                category=scheme.category.value,
                benefit=scheme.benefit_amount,
            )

            # Rule nodes + edges
            for rule in scheme.eligibility_rules:
                rule_node = f"rule_{rule.rule_id}"
                self.graph.add_node(
                    rule_node,
                    node_type="rule",
                    rule_type=rule.rule_type.value,
                    condition=rule.condition,
                    value=rule.value,
                )
                self.graph.add_edge(scheme.scheme_id, rule_node, relation="REQUIRES")

            # Document nodes + edges
            for doc in scheme.required_documents:
                doc_node = f"doc_{doc}"
                if not self.graph.has_node(doc_node):
                    self.graph.add_node(doc_node, node_type="document", doc_type=doc)
                self.graph.add_edge(scheme.scheme_id, doc_node, relation="NEEDS_DOCUMENT")

            # Dependency edges
            for dep_id in scheme.depends_on:
                if dep_id in SCHEME_MAP:
                    self.graph.add_edge(scheme.scheme_id, dep_id, relation="DEPENDS_ON")

            # Conflict edges
            for conflict_id in scheme.conflicts_with:
                if conflict_id in SCHEME_MAP:
                    self.graph.add_edge(scheme.scheme_id, conflict_id, relation="CONFLICTS_WITH")
                    self.graph.add_edge(conflict_id, scheme.scheme_id, relation="CONFLICTS_WITH")

    # ── Eligibility Evaluation ───────────────────────────────────────────

    def evaluate_rule(self, rule: EligibilityRule, citizen: CitizenProfile) -> bool:
        """Evaluate a single eligibility rule against a citizen profile."""
        rt = rule.rule_type
        val = rule.value

        if rt == RuleType.AGE_MIN:
            return (citizen.age or 0) >= int(val)
        if rt == RuleType.AGE_MAX:
            return (citizen.age or 0) <= int(val)
        if rt == RuleType.INCOME_MAX:
            return citizen.annual_income <= float(val)
        if rt == RuleType.GENDER:
            return citizen.gender.value == val
        if rt == RuleType.CASTE:
            allowed = [c.strip() for c in val.split(",")]
            return citizen.caste_category.value in allowed
        if rt == RuleType.STATE:
            return citizen.address.state.lower() == val.lower()
        if rt == RuleType.OCCUPATION:
            allowed = [o.strip() for o in val.split(",")]
            return citizen.occupation.value in allowed
        if rt == RuleType.EDUCATION_MIN:
            return _EDU_ORDER.get(citizen.education.value, 0) >= _EDU_ORDER.get(val, 0)
        if rt == RuleType.EDUCATION_MAX:
            return _EDU_ORDER.get(citizen.education.value, 0) <= _EDU_ORDER.get(val, 0)
        if rt == RuleType.BPL:
            return citizen.is_bpl
        if rt == RuleType.DISABILITY:
            return citizen.is_disabled
        if rt == RuleType.PREGNANT:
            return citizen.is_pregnant
        if rt == RuleType.HAS_CHILDREN:
            return citizen.num_children > 0
        if rt == RuleType.HAS_DAUGHTERS:
            return citizen.num_daughters > 0
        if rt == RuleType.MINORITY:
            return citizen.is_minority

        # Custom rules
        if rt == RuleType.CUSTOM:
            if rule.condition == "child_age_max":
                return any(
                    m.relationship == "child" and m.age <= int(val)
                    for m in citizen.family_members
                )
            if rule.condition == "sc_st_or_female":
                return (
                    citizen.caste_category.value in ("sc", "st")
                    or citizen.gender.value == "female"
                )

        return False

    # ── Scheme Discovery ─────────────────────────────────────────────────

    def discover_schemes(self, citizen: CitizenProfile) -> list[SchemeMatch]:
        """
        Find all schemes a citizen is potentially eligible for.
        Returns ranked list sorted by benefit × approval probability.
        """
        matches: list[SchemeMatch] = []

        for scheme in SCHEMES:
            matched: list[str] = []
            failed: list[str] = []

            for rule in scheme.eligibility_rules:
                if self.evaluate_rule(rule, citizen):
                    matched.append(rule.description or rule.rule_id)
                else:
                    failed.append(rule.description or rule.rule_id)

            total = len(scheme.eligibility_rules)
            score = len(matched) / total if total else 1.0
            is_eligible = len(failed) == 0

            # Find missing documents
            citizen_doc_types = set(citizen.documents)
            missing = [d for d in scheme.required_documents if d not in citizen_doc_types]

            # Detect conflicts
            conflicts = [
                SCHEME_MAP[cid].name
                for cid in scheme.conflicts_with
                if cid in SCHEME_MAP
            ]

            # Benefit chains
            unlocks = self.find_benefit_chain(scheme.scheme_id)

            approval_prob = score * scheme.approval_rate

            matches.append(SchemeMatch(
                scheme=scheme,
                eligibility_score=round(score, 2),
                matched_rules=matched,
                failed_rules=failed,
                missing_documents=missing,
                estimated_benefit=scheme.benefit_amount,
                approval_probability=round(approval_prob, 2),
                is_eligible=is_eligible,
                conflicts=conflicts,
                unlocks=[SCHEME_MAP[uid].name for uid in unlocks if uid in SCHEME_MAP],
            ))

        # Sort by (eligible first, then benefit × approval descending)
        matches.sort(
            key=lambda m: (m.is_eligible, m.estimated_benefit * m.approval_probability),
            reverse=True,
        )

        # Assign ranks
        for i, m in enumerate(matches):
            m.rank = i + 1

        return matches

    # ── Benefit Chain Discovery (multi-hop) ──────────────────────────────

    def find_benefit_chain(self, scheme_id: str, max_hops: int = MAX_HOPS) -> list[str]:
        """
        Follow DEPENDS_ON edges backwards to find schemes that require this
        scheme as a prerequisite (Req 2.5 — up to 5 hops).
        """
        dependents: list[str] = []
        visited: set[str] = {scheme_id}

        frontier = [scheme_id]
        for _ in range(max_hops):
            next_frontier: list[str] = []
            for current in frontier:
                for predecessor in self.graph.predecessors(current):
                    edge_data = self.graph.get_edge_data(predecessor, current)
                    if (
                        edge_data
                        and edge_data.get("relation") == "DEPENDS_ON"
                        and predecessor not in visited
                    ):
                        visited.add(predecessor)
                        dependents.append(predecessor)
                        next_frontier.append(predecessor)
            frontier = next_frontier
            if not frontier:
                break

        return dependents

    # ── Conflict Detection ───────────────────────────────────────────────

    def detect_conflicts(self, scheme_ids: list[str]) -> list[tuple[str, str]]:
        """
        Given a list of scheme IDs the citizen intends to apply for,
        return pairs that conflict (Req 2.4, Property 7).
        """
        conflicts: list[tuple[str, str]] = []
        checked: set[tuple[str, str]] = set()

        for sid in scheme_ids:
            for neighbor in self.graph.successors(sid):
                edge = self.graph.get_edge_data(sid, neighbor)
                if edge and edge.get("relation") == "CONFLICTS_WITH":
                    if neighbor in scheme_ids:
                        pair = tuple(sorted((sid, neighbor)))
                        if pair not in checked:
                            checked.add(pair)
                            conflicts.append(pair)

        return conflicts

    # ── Graph Statistics ─────────────────────────────────────────────────

    def stats(self) -> dict:
        schemes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "scheme"]
        rules = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "rule"]
        docs = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "document"]
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "schemes": len(schemes),
            "rules": len(rules),
            "documents": len(docs),
        }
