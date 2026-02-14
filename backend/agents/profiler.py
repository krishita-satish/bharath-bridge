"""
Profiler Agent — Citizen profile management (Req 1).
Handles profile creation from documents, conflict detection,
DigiLocker simulation, and GDPR-compliant data deletion.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from backend.models.citizen import CitizenProfile, Address, Gender, CasteCategory, EducationLevel, Occupation
from backend.models.document import Document, DocumentType, ExtractionResult


# In-memory citizen store (DynamoDB sim)
_citizens: dict[str, CitizenProfile] = {}


class ProfilerAgent:
    """Creates and manages citizen profiles."""

    def create_profile(self, data: dict) -> CitizenProfile:
        """Create a new citizen profile from form data (Req 1.1)."""
        citizen_id = f"CIT-{uuid.uuid4().hex[:8].upper()}"

        address_data = data.get("address", {})
        address = Address(**address_data) if isinstance(address_data, dict) else Address()

        profile = CitizenProfile(
            citizen_id=citizen_id,
            name=data.get("name", ""),
            date_of_birth=data.get("date_of_birth", ""),
            age=data.get("age"),
            gender=Gender(data.get("gender", "male")),
            aadhaar_number=data.get("aadhaar_number", ""),
            pan_number=data.get("pan_number", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=address,
            caste_category=CasteCategory(data.get("caste_category", "general")),
            religion=data.get("religion", ""),
            annual_income=data.get("annual_income", 0.0),
            occupation=Occupation(data.get("occupation", "other")),
            education=EducationLevel(data.get("education", "none")),
            is_bpl=data.get("is_bpl", False),
            is_disabled=data.get("is_disabled", False),
            disability_percentage=data.get("disability_percentage"),
            is_minority=data.get("is_minority", False),
            is_pregnant=data.get("is_pregnant", False),
            bank_account=data.get("bank_account", ""),
            bank_ifsc=data.get("bank_ifsc", ""),
            documents=data.get("documents", []),
            consent_retention=data.get("consent_retention", False),
        )

        _citizens[citizen_id] = profile
        return profile

    def update_profile(self, citizen_id: str, updates: dict) -> CitizenProfile | None:
        """Update existing citizen profile (Req 1.2)."""
        profile = _citizens.get(citizen_id)
        if not profile:
            return None

        for key, value in updates.items():
            if key == "address" and isinstance(value, dict):
                profile.address = Address(**value)
            elif hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.now().isoformat()
        _citizens[citizen_id] = profile
        return profile

    def get_profile(self, citizen_id: str) -> CitizenProfile | None:
        """Retrieve citizen profile."""
        return _citizens.get(citizen_id)

    def delete_profile(self, citizen_id: str) -> bool:
        """GDPR-compliant data deletion (Req 1.7, 10.4)."""
        if citizen_id in _citizens:
            del _citizens[citizen_id]
            return True
        return False

    def extract_profile_from_documents(
        self, extractions: list[ExtractionResult]
    ) -> dict:
        """
        Build a profile data dict from document extraction results.
        Simulates Bedrock/Textract integration (Req 1.3).
        """
        profile_data: dict = {}

        for ext in extractions:
            fields = ext.extracted_fields

            if ext.document_type == DocumentType.AADHAAR:
                profile_data.update({
                    "name": fields.get("name", ""),
                    "date_of_birth": fields.get("date_of_birth", ""),
                    "gender": fields.get("gender", "male"),
                    "aadhaar_number": fields.get("aadhaar_number", ""),
                    "address": fields.get("address", {}),
                })
            elif ext.document_type == DocumentType.PAN:
                profile_data["pan_number"] = fields.get("pan_number", "")
            elif ext.document_type == DocumentType.INCOME_CERTIFICATE:
                income_str = fields.get("annual_income", "0")
                try:
                    profile_data["annual_income"] = float(str(income_str).replace(",", ""))
                except ValueError:
                    profile_data["annual_income"] = 0.0
            elif ext.document_type == DocumentType.CASTE_CERTIFICATE:
                profile_data["caste_category"] = fields.get("caste_category", "general")
            elif ext.document_type == DocumentType.BANK_STATEMENT:
                profile_data["bank_account"] = fields.get("account_number", "")
                profile_data["bank_ifsc"] = fields.get("ifsc_code", "")

        return profile_data

    def resolve_conflicts(
        self, profile: CitizenProfile, new_data: dict
    ) -> dict:
        """
        Detect and resolve conflicts between existing profile and new data.
        Returns conflict report (Req 1.4).
        """
        conflicts: list[dict] = []
        merged: dict = {}

        for key, new_val in new_data.items():
            if key in ("citizen_id", "created_at"):
                continue
            old_val = getattr(profile, key, None)
            if old_val and old_val != new_val and new_val:
                conflicts.append({
                    "field": key,
                    "existing_value": str(old_val),
                    "new_value": str(new_val),
                    "resolution": "new_value_preferred",
                })
                merged[key] = new_val
            elif new_val:
                merged[key] = new_val

        return {
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0,
            "merged_updates": merged,
        }

    def list_profiles(self) -> list[CitizenProfile]:
        """List all stored citizen profiles."""
        return list(_citizens.values())
