"""
Rejection prediction model — simulates XGBoost/SageMaker prediction.
Encodes citizen + scheme features into a numeric vector and predicts
rejection probability (Req 4).
"""

from __future__ import annotations

import random
from backend.models.citizen import CitizenProfile
from backend.models.scheme import Scheme


def _encode_features(citizen: CitizenProfile, scheme: Scheme) -> list[float]:
    """Encode citizen + scheme into a feature vector for prediction."""
    missing_docs = len([
        d for d in scheme.required_documents if d not in set(citizen.documents)
    ])
    total_docs = len(scheme.required_documents)
    doc_completeness = 1.0 - (missing_docs / total_docs) if total_docs else 1.0

    has_aadhaar = 1.0 if citizen.aadhaar_number else 0.0
    has_bank = 1.0 if citizen.bank_account else 0.0

    income_ratio = 0.0
    for rule in scheme.eligibility_rules:
        if rule.rule_type.value == "income_max":
            max_val = float(rule.value)
            income_ratio = citizen.annual_income / max_val if max_val else 0.0
            break

    age_risk = 0.0
    if citizen.age:
        for rule in scheme.eligibility_rules:
            if rule.rule_type.value in ("age_min", "age_max"):
                limit = int(rule.value)
                diff = abs(citizen.age - limit)
                if diff <= 2:
                    age_risk = 1.0 - diff * 0.3

    return [
        doc_completeness,
        has_aadhaar,
        has_bank,
        income_ratio,
        age_risk,
        scheme.approval_rate,
        len(citizen.family_members) / 10.0,
    ]


def predict_rejection_probability(
    citizen: CitizenProfile, scheme: Scheme
) -> float:
    """
    Simulate an XGBoost model predicting rejection probability.
    In production, this calls SageMaker; for demo it uses weighted features.
    """
    features = _encode_features(citizen, scheme)

    weights = [0.30, 0.15, 0.10, 0.15, 0.10, 0.15, 0.05]

    # The score is the complementary risk aggregate
    positive_score = sum(f * w for f, w in zip(features, weights))

    # Add a tiny random factor to simulate real model variance
    noise = random.uniform(-0.03, 0.03)
    rejection_prob = max(0.0, min(1.0, 1.0 - positive_score + noise))

    return round(rejection_prob, 3)
