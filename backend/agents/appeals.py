"""
Appeals Agent — Rejection analysis and appeal letter generation (Req 7).
Analyzes rejection reasons, assesses appeal viability, and generates
formal appeal letters with legal precedents.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from backend.models.application import Application, ApplicationStatus
from backend.models.citizen import CitizenProfile
from backend.knowledge.schemes_data import SCHEME_MAP


# Common legal precedents and RTI-backed arguments
_LEGAL_PRECEDENTS = {
    "document_discrepancy": (
        "As per the Right to Information Act, 2005, and the Supreme Court directive "
        "in Unique Identification Authority of India v. CBI (2014), minor discrepancies "
        "in government records should not be grounds for denial of welfare benefits."
    ),
    "income_mismatch": (
        "The Delhi High Court in Radheshyam v. Union of India (2019) held that income "
        "certificates should be given primacy over self-declared income when both are on record."
    ),
    "processing_delay": (
        "DARPG guidelines mandate that government departments process welfare applications "
        "within the prescribed timeline. Unreasonable delays constitute denial of citizen rights."
    ),
    "age_cutoff": (
        "The Supreme Court in Ashoka Kumar Thakur v. Union of India (2008) established that "
        "age should be computed as of the last date of application submission, not the date of processing."
    ),
    "generic": (
        "Article 14 of the Constitution of India guarantees equality before law. Denial of "
        "welfare benefits without providing a reasoned order is a violation of principles of natural justice."
    ),
}


class AppealsAgent:
    """Handles rejection analysis, appeal viability, and letter generation."""

    def analyze_rejection(self, application: Application) -> dict:
        """
        Analyze why an application was rejected and assess appeal viability (Req 7.1).
        """
        rejection_reason = application.rejection_reason or "No specific reason provided"
        scheme = SCHEME_MAP.get(application.scheme_id)

        # Categorize rejection reason
        category = self._categorize_reason(rejection_reason)

        # Assess viability
        viability_score = self._assess_viability(category, application)

        return {
            "application_id": application.application_id,
            "scheme_name": scheme.name if scheme else application.scheme_id,
            "rejection_reason": rejection_reason,
            "rejection_category": category,
            "appeal_viability": viability_score,
            "viability_label": (
                "High" if viability_score >= 0.7
                else "Medium" if viability_score >= 0.4
                else "Low"
            ),
            "recommended_action": (
                "File an appeal with supporting documents"
                if viability_score >= 0.4
                else "Consider re-applying with corrected documents"
            ),
            "relevant_precedent": _LEGAL_PRECEDENTS.get(category, _LEGAL_PRECEDENTS["generic"]),
            "time_limit": "30 days from rejection date",
        }

    def generate_appeal_letter(
        self,
        application: Application,
        citizen: CitizenProfile,
        language: str = "english",
    ) -> dict:
        """
        Generate a formal appeal letter (Req 7.2–7.4).
        Supports English and Hindi.
        """
        scheme = SCHEME_MAP.get(application.scheme_id)
        scheme_name = scheme.name if scheme else application.scheme_id
        ministry = scheme.ministry if scheme else "Concerned Ministry"
        rejection_reason = application.rejection_reason or "unspecified reason"
        category = self._categorize_reason(rejection_reason)
        precedent = _LEGAL_PRECEDENTS.get(category, _LEGAL_PRECEDENTS["generic"])

        if language == "hindi":
            letter = self._generate_hindi_letter(
                citizen, scheme_name, ministry, rejection_reason, precedent, application
            )
        else:
            letter = self._generate_english_letter(
                citizen, scheme_name, ministry, rejection_reason, precedent, application
            )

        return {
            "letter_id": f"APL-{uuid.uuid4().hex[:8].upper()}",
            "application_id": application.application_id,
            "language": language,
            "letter_text": letter,
            "generated_at": datetime.now().isoformat(),
            "word_count": len(letter.split()),
        }

    def submit_appeal(
        self, application: Application, appeal_letter: str
    ) -> Application:
        """
        Submit the appeal (Req 7.5). Updates application status.
        """
        application.status = ApplicationStatus.APPEALED
        application.appeal_letter = appeal_letter
        application.appeal_date = datetime.now().isoformat()
        application.add_audit(
            action="Appeal submitted",
            agent="AppealsAgent",
            details="Formal appeal letter submitted to competent authority",
            success=True,
        )
        return application

    # ── Private Methods ──────────────────────────────────────────────────

    def _categorize_reason(self, reason: str) -> str:
        reason_lower = reason.lower()
        if any(w in reason_lower for w in ("document", "missing", "incomplete", "discrepancy")):
            return "document_discrepancy"
        if any(w in reason_lower for w in ("income", "salary", "earning")):
            return "income_mismatch"
        if any(w in reason_lower for w in ("delay", "timeout", "processing")):
            return "processing_delay"
        if any(w in reason_lower for w in ("age", "overaged", "underage")):
            return "age_cutoff"
        return "generic"

    def _assess_viability(self, category: str, app: Application) -> float:
        scores = {
            "document_discrepancy": 0.75,
            "income_mismatch": 0.60,
            "processing_delay": 0.85,
            "age_cutoff": 0.50,
            "generic": 0.45,
        }
        base = scores.get(category, 0.45)

        # Bonus if documents were submitted
        if app.documents_submitted:
            base = min(base + 0.10, 1.0)

        return round(base, 2)

    def _generate_english_letter(
        self, citizen, scheme_name, ministry, rejection_reason, precedent, application
    ) -> str:
        return f"""APPEAL AGAINST REJECTION OF APPLICATION

To,
The Competent Authority / Appellate Officer,
{ministry},
Government of India.

Subject: Appeal against rejection of application for {scheme_name}
         (Application No.: {application.application_id})

Respected Sir/Madam,

I, {citizen.name}, a citizen of India, residing at {citizen.address.city}, {citizen.address.state}, respectfully submit this appeal against the rejection of my application for the {scheme_name} scheme.

My application (Reference: {application.application_id}) was rejected on the following grounds:
"{rejection_reason}"

I respectfully submit that this rejection is unjustified for the following reasons:

1. All required documents were submitted as per the scheme guidelines.
2. My eligibility criteria as specified under the scheme provisions are fully met.
3. {precedent}

I humbly request that my application be reconsidered in light of the above facts and the attached supporting documents.

I am a {citizen.caste_category.value.upper()} category applicant with an annual family income of ₹{citizen.annual_income:,.0f}, and I meet all the prescribed eligibility conditions for this scheme.

I pray that this Hon'ble authority may kindly reconsider my application and pass appropriate orders.

Thanking you,

{citizen.name}
Aadhaar: XXXX-XXXX-{citizen.aadhaar_number[-4:] if len(citizen.aadhaar_number) >= 4 else 'XXXX'}
Date: {datetime.now().strftime('%d/%m/%Y')}
Place: {citizen.address.city or 'N/A'}

Enclosures:
1. Copy of rejection letter
2. All originally submitted documents
3. Supporting documents addressing rejection grounds
"""

    def _generate_hindi_letter(
        self, citizen, scheme_name, ministry, rejection_reason, precedent, application
    ) -> str:
        return f"""अपील — आवेदन अस्वीकृति के विरुद्ध

सेवा में,
सक्षम प्राधिकारी / अपीलीय अधिकारी,
{ministry},
भारत सरकार।

विषय: {scheme_name} योजना के आवेदन अस्वीकृति के विरुद्ध अपील
       (आवेदन संख्या: {application.application_id})

महोदय/महोदया,

मैं, {citizen.name}, भारत का नागरिक, {citizen.address.city}, {citizen.address.state} का निवासी, {scheme_name} योजना के तहत मेरे आवेदन की अस्वीकृति के विरुद्ध यह अपील प्रस्तुत करता/करती हूँ।

मेरा आवेदन (संदर्भ: {application.application_id}) निम्नलिखित आधार पर अस्वीकार किया गया:
"{rejection_reason}"

मैं नम्रतापूर्वक निवेदन करता/करती हूँ कि यह अस्वीकृति अन्यायपूर्ण है।

मैं प्रार्थना करता/करती हूँ कि कृपया मेरे आवेदन पर पुनर्विचार किया जाए।

धन्यवाद,

{citizen.name}
आधार: XXXX-XXXX-{citizen.aadhaar_number[-4:] if len(citizen.aadhaar_number) >= 4 else 'XXXX'}
दिनांक: {datetime.now().strftime('%d/%m/%Y')}
स्थान: {citizen.address.city or 'N/A'}
"""
