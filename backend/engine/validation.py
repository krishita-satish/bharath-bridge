"""
Adversarial validation engine — simulates rejection risk analysis.
Evaluates applications against known rejection patterns (Req 4).
"""

from __future__ import annotations

from backend.models.citizen import CitizenProfile
from backend.models.scheme import Scheme
from backend.models.application import RejectionAnalysis


# Common government rejection patterns sourced from RTI data
REJECTION_PATTERNS: list[dict] = [
    {
        "id": "incomplete_docs",
        "name": "Incomplete Documentation",
        "weight": 0.30,
        "description": "Missing or expired mandatory documents",
    },
    {
        "id": "income_mismatch",
        "name": "Income Certificate Mismatch",
        "weight": 0.20,
        "description": "Declared income differs from income certificate",
    },
    {
        "id": "aadhaar_bank_mismatch",
        "name": "Aadhaar-Bank Name Mismatch",
        "weight": 0.15,
        "description": "Name on Aadhaar doesn't match bank account name",
    },
    {
        "id": "address_mismatch",
        "name": "Address / Domicile Mismatch",
        "weight": 0.10,
        "description": "Address on documents doesn't match domicile certificate",
    },
    {
        "id": "age_boundary",
        "name": "Age Boundary Issue",
        "weight": 0.10,
        "description": "Applicant's age is at the boundary of eligibility cutoff",
    },
    {
        "id": "duplicate_application",
        "name": "Duplicate Application Detected",
        "weight": 0.10,
        "description": "Existing active application for the same scheme",
    },
    {
        "id": "caste_cert_expired",
        "name": "Caste Certificate Validity",
        "weight": 0.05,
        "description": "Caste certificate older than 6 months",
    },
]


def _check_missing_docs(citizen: CitizenProfile, scheme: Scheme) -> list[str]:
    """Return list of missing required documents."""
    citizen_docs = set(citizen.documents)
    return [d for d in scheme.required_documents if d not in citizen_docs]


def predict_rejection(
    citizen: CitizenProfile,
    scheme: Scheme,
    existing_application_ids: list[str] | None = None,
) -> RejectionAnalysis:
    """
    Predict rejection probability and identify risk factors.
    Returns a RejectionAnalysis with actionable recommendations.
    """
    risk_factors: list[dict] = []
    total_risk: float = 0.0

    # 1. Incomplete documentation
    missing = _check_missing_docs(citizen, scheme)
    if missing:
        factor_risk = 0.30 * (len(missing) / max(len(scheme.required_documents), 1))
        risk_factors.append({
            "factor": "Incomplete Documentation",
            "severity": "high" if len(missing) > 2 else "medium",
            "details": f"Missing documents: {', '.join(missing)}",
            "risk_contribution": round(factor_risk, 2),
        })
        total_risk += factor_risk

    # 2. Income verification risk
    if citizen.annual_income > 0:
        for rule in scheme.eligibility_rules:
            if rule.rule_type.value == "income_max":
                max_income = float(rule.value)
                ratio = citizen.annual_income / max_income if max_income else 0
                if ratio > 0.85:
                    factor_risk = 0.20 * min(ratio - 0.85, 0.15) / 0.15
                    risk_factors.append({
                        "factor": "Income Near Threshold",
                        "severity": "high" if ratio > 0.95 else "medium",
                        "details": f"Income ₹{citizen.annual_income:,.0f} is {ratio*100:.0f}% of max ₹{max_income:,.0f}",
                        "risk_contribution": round(factor_risk, 2),
                    })
                    total_risk += factor_risk

    # 3. Aadhaar presence check
    if not citizen.aadhaar_number:
        risk_factors.append({
            "factor": "Missing Aadhaar",
            "severity": "critical",
            "details": "Aadhaar number not provided — required for DBT",
            "risk_contribution": 0.25,
        })
        total_risk += 0.25

    # 4. Bank account verification
    if not citizen.bank_account:
        risk_factors.append({
            "factor": "No Bank Account Linked",
            "severity": "high",
            "details": "Bank account needed for benefit disbursement via DBT",
            "risk_contribution": 0.15,
        })
        total_risk += 0.15

    # 5. Age boundary risk
    if citizen.age:
        for rule in scheme.eligibility_rules:
            if rule.rule_type.value in ("age_min", "age_max"):
                limit = int(rule.value)
                diff = abs(citizen.age - limit)
                if diff <= 1:
                    risk_factors.append({
                        "factor": "Age Boundary Risk",
                        "severity": "medium",
                        "details": f"Age {citizen.age} is at the boundary of limit {limit}",
                        "risk_contribution": 0.08,
                    })
                    total_risk += 0.08

    # 6. Base risk from scheme's historical rejection rate
    base_rejection = 1 - scheme.approval_rate
    total_risk += base_rejection * 0.3

    # Clamp to [0, 1]
    total_risk = min(max(total_risk, 0.0), 1.0)

    # Risk level
    if total_risk >= 0.7:
        risk_level = "critical"
    elif total_risk >= 0.5:
        risk_level = "high"
    elif total_risk >= 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"

    # Generate recommendations
    recommendations = _generate_recommendations(risk_factors, missing)

    return RejectionAnalysis(
        rejection_probability=round(total_risk, 2),
        risk_level=risk_level,
        risk_factors=risk_factors,
        recommendations=recommendations,
        common_rejection_patterns=[p["name"] for p in REJECTION_PATTERNS[:3]],
    )


def _generate_recommendations(
    risk_factors: list[dict], missing_docs: list[str]
) -> list[str]:
    """Generate actionable fix recommendations based on risk factors."""
    recs: list[str] = []

    for factor in risk_factors:
        name = factor["factor"]
        if "Documentation" in name:
            for doc in missing_docs:
                recs.append(f"Upload your {doc.replace('_', ' ')} before submitting")
        elif "Aadhaar" in name:
            recs.append("Link your Aadhaar number — this is mandatory for Direct Benefit Transfer")
        elif "Bank" in name:
            recs.append("Open a Jan Dhan account if you don't have one — it's zero-balance and free")
        elif "Income" in name:
            recs.append("Ensure income certificate matches your actual declared income to avoid mismatch")
        elif "Age" in name:
            recs.append("Submit application before your birthdate crosses the age cutoff")

    # Dedup
    return list(dict.fromkeys(recs))
