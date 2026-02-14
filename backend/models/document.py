"""Document intelligence data models (Req 3)."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """All 7 supported document types (Req 3.7)."""
    AADHAAR = "aadhaar"
    PAN = "pan"
    INCOME_CERTIFICATE = "income_certificate"
    CASTE_CERTIFICATE = "caste_certificate"
    DOMICILE_CERTIFICATE = "domicile_certificate"
    BANK_STATEMENT = "bank_statement"
    EDUCATIONAL_CERTIFICATE = "educational_certificate"
    BIRTH_CERTIFICATE = "birth_certificate"
    DISABILITY_CERTIFICATE = "disability_certificate"
    BPL_CARD = "bpl_card"
    RATION_CARD = "ration_card"
    VOTER_ID = "voter_id"
    PASSPORT_PHOTO = "passport_photo"


class AuthenticityStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


class ExtractionResult(BaseModel):
    """Structured data extracted from a document (simulating Textract)."""

    document_type: DocumentType
    extracted_fields: dict = Field(default_factory=dict)
    confidence: float = 0.0  # 0.0–1.0
    raw_text: str = ""


class ValidationIssue(BaseModel):
    field: str = ""
    issue: str = ""
    severity: str = "warning"  # warning / error
    suggestion: str = ""


class Document(BaseModel):
    """A citizen document with extraction and validation results."""

    document_id: str = Field(default="")
    citizen_id: str = ""
    document_type: DocumentType
    file_name: str = ""
    file_path: str = ""  # S3 key in production
    file_size: int = 0

    # Extraction
    extraction_result: Optional[ExtractionResult] = None
    extracted_at: Optional[str] = None

    # Validation
    authenticity_status: AuthenticityStatus = AuthenticityStatus.PENDING
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    validated_at: Optional[str] = None

    # Metadata
    issuing_authority: str = ""
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None

    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )

    @property
    def is_valid(self) -> bool:
        return (
            self.authenticity_status == AuthenticityStatus.VERIFIED
            and not any(i.severity == "error" for i in self.validation_issues)
        )

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.validation_issues)


# Required fields per document type for extraction completeness (Property 1)
REQUIRED_FIELDS: dict[DocumentType, list[str]] = {
    DocumentType.AADHAAR: [
        "aadhaar_number", "name", "date_of_birth", "address", "gender"
    ],
    DocumentType.PAN: [
        "pan_number", "name", "date_of_birth", "father_name"
    ],
    DocumentType.INCOME_CERTIFICATE: [
        "certificate_number", "name", "annual_income",
        "issuing_authority", "validity_period"
    ],
    DocumentType.CASTE_CERTIFICATE: [
        "certificate_number", "name", "caste_category",
        "issuing_authority"
    ],
    DocumentType.DOMICILE_CERTIFICATE: [
        "certificate_number", "name", "state", "district",
        "issuing_authority"
    ],
    DocumentType.BANK_STATEMENT: [
        "account_number", "account_holder", "bank_name",
        "ifsc_code", "balance"
    ],
    DocumentType.EDUCATIONAL_CERTIFICATE: [
        "certificate_type", "institution", "name",
        "year_of_passing", "percentage_or_grade"
    ],
}
