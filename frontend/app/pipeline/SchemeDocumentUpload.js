import { useState, useEffect } from "react";

// Scheme Document Requirements Mapping
// Matches keys from backend/knowledge/schemes_data.py
const SCHEME_DOCUMENTS = {
    pm_kisan: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "bank_statement", label: "Bank Account Proof" },
        { type: "income_certificate", label: "Land Ownership / Income Proof" }
    ],
    pm_ujjwala: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "bpl_card", label: "BPL Card" },
        { type: "bank_statement", label: "Bank Passbook" }
    ],
    pmay: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "income_certificate", label: "Income Certificate" },
        { type: "bpl_card", label: "BPL Card" },
        { type: "bank_statement", label: "Bank Statement" }
    ],
    pm_jan_dhan: [
        { type: "aadhaar", label: "Aadhaar Card" }
    ],
    sukanya_samriddhi: [
        { type: "aadhaar", label: "Parent/Guardian Aadhaar" },
        { type: "birth_certificate", label: "Girl Child Birth Certificate" },
        { type: "bank_statement", label: "Initial Deposit Proof" }
    ],
    beti_bachao: [
        { type: "aadhaar", label: "Parent/Guardian Aadhaar" },
        { type: "birth_certificate", label: "Girl Child Birth Certificate" },
        { type: "income_certificate", label: "Income Certificate" }
    ],
    pm_matru_vandana: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "bank_statement", label: "Bank Passbook" },
        { type: "income_certificate", label: "MCP Card / Income Proof" }
    ],
    nsap_pension: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "bpl_card", label: "BPL Card" },
        { type: "bank_statement", label: "Bank Passbook" },
        { type: "income_certificate", label: "Age Proof / Income Certificate" }
    ],
    atal_pension: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "bank_statement", label: "Savings Account Proof" }
    ],
    national_scholarship: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "caste_certificate", label: "Caste Certificate" },
        { type: "income_certificate", label: "Income Certificate" },
        { type: "educational_certificate", label: "Previous Marksheet" },
        { type: "bank_statement", label: "Bank Passbook" }
    ],
    ayushman_bharat: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "ration_card", label: "Ration Card" },
        { type: "income_certificate", label: "Income Certificate" }
    ],
    mudra_loan: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "pan", label: "PAN Card" },
        { type: "bank_statement", label: "Business Address Proof" },
        { type: "income_certificate", label: "ITR / Income Proof" }
    ],
    disability_pension: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "disability_certificate", label: "Disability Certificate" },
        { type: "bpl_card", label: "BPL Card" },
        { type: "bank_statement", label: "Bank Passbook" }
    ],
    nfsa_ration: [
        { type: "aadhaar", label: "Head of Family Aadhaar" },
        { type: "ration_card", label: "Old Ration Card / Application" },
        { type: "income_certificate", label: "Income Certificate" }
    ],
    standup_india: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "pan", label: "PAN Card" },
        { type: "caste_certificate", label: "Caste Certificate (if applicable)" },
        { type: "bank_statement", label: "Project Report / Bank Proof" },
        { type: "income_certificate", label: "Income Proof" }
    ],
    pm_fasal_bima: [
        { type: "aadhaar", label: "Aadhaar Card" },
        { type: "bank_statement", label: "Land Possession Certificate (LPC)" },
        { type: "income_certificate", label: "Sowing Certificate" }
    ]
};

export default function SchemeDocumentUpload({ schemeId, onDocumentsChange }) {
    const [uploads, setUploads] = useState({});
    const [errors, setErrors] = useState({});

    const requiredDocs = SCHEME_DOCUMENTS[schemeId] || [];

    // Reset uploads when scheme changes
    useEffect(() => {
        setUploads({});
        setErrors({});
        if (onDocumentsChange) onDocumentsChange([]);
    }, [schemeId]);

    // Update parent when valid uploads change
    useEffect(() => {
        const validDocs = requiredDocs
            .filter(doc => uploads[doc.type])
            .map(doc => doc.type);

        if (onDocumentsChange) {
            onDocumentsChange(validDocs);
        }
    }, [uploads, schemeId]);

    const handleFileChange = (docType, e) => {
        const file = e.target.files[0];

        // Clear previous errors/uploads for this field
        const newErrors = { ...errors };
        delete newErrors[docType];
        setErrors(newErrors);

        if (!file) {
            const newUploads = { ...uploads };
            delete newUploads[docType];
            setUploads(newUploads);
            return;
        }

        // Validation
        if (file.type !== "application/pdf") {
            setErrors(prev => ({ ...prev, [docType]: "Only PDF files allowed" }));
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB
            setErrors(prev => ({ ...prev, [docType]: "File exceeds 10MB limit" }));
            return;
        }

        // Success
        setUploads(prev => ({ ...prev, [docType]: file.name }));
    };

    const removeFile = (docType) => {
        setUploads(prev => {
            const next = { ...prev };
            delete next[docType];
            return next;
        });
        setErrors(prev => {
            const next = { ...prev };
            delete next[docType];
            return next;
        });

        // Reset file input value
        const input = document.getElementById(`file-upload-${docType}`);
        if (input) input.value = "";
    };

    if (requiredDocs.length === 0) return null;

    return (
        <div className="card" style={{ marginTop: 16, border: "1px solid var(--border-color)", padding: 16 }}>
            <h4 style={{ marginBottom: 16, fontSize: "1rem", fontWeight: 600 }}>
                Required Documents for Selected Scheme
            </h4>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {requiredDocs.map((doc) => (
                    <div key={doc.type} style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        <label style={{ fontSize: "0.875rem", fontWeight: 500, color: "var(--text-main)" }}>
                            {doc.label} <span style={{ color: "red" }}>*</span>
                        </label>

                        {!uploads[doc.type] ? (
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                <input
                                    id={`file-upload-${doc.type}`}
                                    type="file"
                                    accept=".pdf"
                                    onChange={(e) => handleFileChange(doc.type, e)}
                                    style={{
                                        fontSize: "0.875rem",
                                        padding: "8px",
                                        border: "1px solid var(--border-color)",
                                        borderRadius: 4,
                                        width: "100%",
                                        background: "var(--bg-input)"
                                    }}
                                />
                            </div>
                        ) : (
                            <div style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                padding: "8px 12px",
                                background: "rgba(34, 197, 94, 0.1)",
                                border: "1px solid rgba(34, 197, 94, 0.2)",
                                borderRadius: 4
                            }}>
                                <span style={{ fontSize: "0.875rem", color: "var(--text-main)", display: "flex", alignItems: "center", gap: 6 }}>
                                    📄 {uploads[doc.type]}
                                </span>
                                <button
                                    onClick={() => removeFile(doc.type)}
                                    style={{
                                        background: "none",
                                        border: "none",
                                        color: "var(--accent-red)",
                                        cursor: "pointer",
                                        fontSize: "0.875rem",
                                        textDecoration: "underline"
                                    }}
                                >
                                    Remove
                                </button>
                            </div>
                        )}

                        {errors[doc.type] && (
                            <span style={{ fontSize: "0.75rem", color: "var(--accent-red)" }}>
                                ⚠️ {errors[doc.type]}
                            </span>
                        )}
                        {!errors[doc.type] && !uploads[doc.type] && (
                            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                                PDF only, max 10 MB
                            </span>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
