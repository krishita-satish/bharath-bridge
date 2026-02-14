"""
Adversarial Agent — Rejection prediction engine (Req 4).
Uses the validation engine and rejection model to predict rejection
probability, identify risk factors, and generate recommendations.
"""

from __future__ import annotations

from backend.models.citizen import CitizenProfile
from backend.models.scheme import Scheme
from backend.models.application import Application, RejectionAnalysis
from backend.engine.validation import predict_rejection
from backend.engine.rejection_model import predict_rejection_probability
from backend.knowledge.schemes_data import SCHEME_MAP


class AdversarialAgent:
    """Predicts rejection risks and generates fix recommendations."""

    def predict_rejection(
        self,
        citizen: CitizenProfile,
        scheme_id: str,
    ) -> RejectionAnalysis | None:
        """
        Run full adversarial analysis on a citizen–scheme pair (Req 4.1–4.3).
        Combines rule-based analysis with ML model prediction.
        """
        scheme = SCHEME_MAP.get(scheme_id)
        if not scheme:
            return None

        # Rule-based analysis
        analysis = predict_rejection(citizen, scheme)

        # ML model prediction (simulated)
        ml_prob = predict_rejection_probability(citizen, scheme)

        # Combine: weighted average (60% rule-based, 40% ML)
        combined = analysis.rejection_probability * 0.6 + ml_prob * 0.4
        analysis.rejection_probability = round(combined, 2)

        # Re-classify risk level based on combined score
        if combined >= 0.7:
            analysis.risk_level = "critical"
        elif combined >= 0.5:
            analysis.risk_level = "high"
        elif combined >= 0.3:
            analysis.risk_level = "medium"
        else:
            analysis.risk_level = "low"

        return analysis

    def generate_recommendations(
        self, analysis: RejectionAnalysis
    ) -> list[str]:
        """
        Generate actionable fix recommendations based on risk factors (Req 4.4).
        """
        recs = list(analysis.recommendations)

        if analysis.risk_level in ("high", "critical"):
            recs.insert(0, "⚠ HIGH RISK — Address the following issues before submitting:")

        if analysis.rejection_probability > 0.5:
            recs.append(
                "Consider applying through a Common Service Centre (CSC) for assisted form-filling"
            )

        return recs

    def update_prediction(
        self,
        citizen: CitizenProfile,
        scheme_id: str,
        corrections: dict,
    ) -> RejectionAnalysis | None:
        """
        Re-run prediction after citizen applies corrections (Req 4.5).
        Applies corrections to a copy of the profile and re-predicts.
        """
        # Apply corrections to a copy
        updated_data = citizen.model_dump()
        updated_data.update(corrections)
        updated_citizen = CitizenProfile(**updated_data)

        return self.predict_rejection(updated_citizen, scheme_id)

    def batch_predict(
        self,
        citizen: CitizenProfile,
        scheme_ids: list[str],
    ) -> dict[str, RejectionAnalysis]:
        """
        Predict rejection for multiple schemes at once.
        Returns a dict of scheme_id → analysis.
        """
        results: dict[str, RejectionAnalysis] = {}
        for sid in scheme_ids:
            analysis = self.predict_rejection(citizen, sid)
            if analysis:
                results[sid] = analysis
        return results
