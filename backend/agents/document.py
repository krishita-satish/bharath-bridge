"""
Document Agent — Document intelligence and validation (Req 3).
Simulates AWS Textract for extraction, validates authenticity,
supports PII redaction, and handles all 7+ document types.
"""

from __future__ import annotations

import uuid
import re
import random
from datetime import datetime

from backend.models.document import (
    Document, DocumentType, ExtractionResult, ValidationIssue,
    AuthenticityStatus, REQUIRED_FIELDS,
)


# Simulated extraction templates per document type
_EXTRACTION_TEMPLATES: dict[DocumentType, dict] = {
    DocumentType.AADHAAR: {
        "aadhaar_number": "XXXX-XXXX-{rand4}",
        "name": "Demo Citizen",
        "date_of_birth": "1990-01-15",
        "address": {"city": "New Delhi", "state": "Delhi", "pincode": "110001"},
        "gender": "male",
    },
    DocumentType.PAN: {
        "pan_number": "ABCDE{rand4}F",
        "name": "Demo Citizen",
        "date_of_birth": "1990-01-15",
        "father_name": "Demo Father",
    },
    DocumentType.INCOME_CERTIFICATE: {
        "certificate_number": "INC-{rand6}",
        "name": "Demo Citizen",
        "annual_income": "200000",
        "issuing_authority": "Tehsildar, District Revenue Office",
        "validity_period": "6 months",
    },
    DocumentType.CASTE_CERTIFICATE: {
        "certificate_number": "CST-{rand6}",
        "name": "Demo Citizen",
        "caste_category": "obc",
        "issuing_authority": "District Magistrate Office",
    },
    DocumentType.DOMICILE_CERTIFICATE: {
        "certificate_number": "DOM-{rand6}",
        "name": "Demo Citizen",
        "state": "Delhi",
        "district": "New Delhi",
        "issuing_authority": "SDM Office",
    },
    DocumentType.BANK_STATEMENT: {
        "account_number": "ACC{rand8}",
        "account_holder": "Demo Citizen",
        "bank_name": "State Bank of India",
        "ifsc_code": "SBIN0001234",
        "balance": "50000",
    },
    DocumentType.EDUCATIONAL_CERTIFICATE: {
        "certificate_type": "Post-Matric",
        "institution": "Delhi University",
        "name": "Demo Citizen",
        "year_of_passing": "2023",
        "percentage_or_grade": "78%",
    },
}


class DocumentAgent:
    """Handles document extraction, validation, and PII redaction."""

    def extract_document_data(
        self, doc_type: DocumentType, file_name: str = ""
    ) -> Document:
        """
        Simulate Textract extraction for a document (Req 3.1–3.3).
        Returns a Document with extraction results.
        """
        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"

        # Get template and fill random values
        template = _EXTRACTION_TEMPLATES.get(doc_type, {})
        fields: dict = {}
        for key, val in template.items():
            if isinstance(val, str):
                val = val.replace("{rand4}", str(random.randint(1000, 9999)))
                val = val.replace("{rand6}", str(random.randint(100000, 999999)))
                val = val.replace("{rand8}", str(random.randint(10000000, 99999999)))
            fields[key] = val

        confidence = round(random.uniform(0.85, 0.99), 2)

        extraction = ExtractionResult(
            document_type=doc_type,
            extracted_fields=fields,
            confidence=confidence,
            raw_text=f"Simulated OCR text for {doc_type.value} document",
        )

        document = Document(
            document_id=doc_id,
            document_type=doc_type,
            file_name=file_name or f"{doc_type.value}_scan.pdf",
            extraction_result=extraction,
            extracted_at=datetime.now().isoformat(),
        )

        return document

    def validate_authenticity(self, document: Document) -> Document:
        """
        Validate document authenticity and completeness (Req 3.4–3.5).
        Checks required fields and formats.
        """
        issues: list[ValidationIssue] = []

        if not document.extraction_result:
            document.authenticity_status = AuthenticityStatus.FAILED
            issues.append(ValidationIssue(
                field="extraction",
                issue="No extraction result available",
                severity="error",
                suggestion="Re-upload the document with better quality",
            ))
            document.validation_issues = issues
            return document

        fields = document.extraction_result.extracted_fields
        required = REQUIRED_FIELDS.get(document.document_type, [])

        # Check completeness
        for field_name in required:
            if field_name not in fields or not fields[field_name]:
                issues.append(ValidationIssue(
                    field=field_name,
                    issue=f"Required field '{field_name}' missing or empty",
                    severity="error",
                    suggestion=f"Ensure {field_name.replace('_', ' ')} is clearly visible in the document scan",
                ))

        # Check confidence
        if document.extraction_result.confidence < 0.8:
            issues.append(ValidationIssue(
                field="confidence",
                issue=f"Low extraction confidence: {document.extraction_result.confidence:.0%}",
                severity="warning",
                suggestion="Re-upload a clearer scan (300 DPI recommended)",
            ))

        # Aadhaar format validation
        if document.document_type == DocumentType.AADHAAR:
            aadhaar = fields.get("aadhaar_number", "")
            if aadhaar and not re.match(r"\d{4}[-\s]?\d{4}[-\s]?\d{4}", aadhaar.replace("X", "0")):
                issues.append(ValidationIssue(
                    field="aadhaar_number",
                    issue="Aadhaar number format invalid",
                    severity="warning",
                    suggestion="Aadhaar should be a 12-digit number",
                ))

        # Set status
        has_errors = any(i.severity == "error" for i in issues)
        if has_errors:
            document.authenticity_status = AuthenticityStatus.FAILED
        elif issues:
            document.authenticity_status = AuthenticityStatus.MANUAL_REVIEW
        else:
            document.authenticity_status = AuthenticityStatus.VERIFIED

        document.validation_issues = issues
        document.validated_at = datetime.now().isoformat()
        return document

    def redact_pii(self, text: str) -> str:
        """
        Redact PII from text (Req 3.6, 10.2).
        Masks Aadhaar numbers, PAN, phone numbers, emails, bank accounts.
        """
        # Aadhaar: 12 digits (with optional spaces/dashes)
        text = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "XXXX-XXXX-XXXX", text)
        # PAN: 5 letters + 4 digits + 1 letter
        text = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]\b", "XXXXX0000X", text)
        # Phone: 10 digits
        text = re.sub(r"\b\d{10}\b", "XXXXXXXXXX", text)
        # Email
        text = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "***@***.***",
            text,
        )
        # Bank account (8–18 digits)
        text = re.sub(r"\b\d{8,18}\b", "XXXXXXXX", text)

        return text

    def process_document(
        self, doc_type: DocumentType, file_name: str = ""
    ) -> Document:
        """Full pipeline: extract → validate → return."""
        doc = self.extract_document_data(doc_type, file_name)
        doc = self.validate_authenticity(doc)
        return doc
