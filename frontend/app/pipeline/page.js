"use client";
import { useState } from "react";

const API = "http://127.0.0.1:8000";

const STAGES = [
    { key: "profile", label: "Profiler Agent", icon: "👤", desc: "Creating citizen profile" },
    { key: "eligibility", label: "Eligibility Agent", icon: "🎯", desc: "Discovering eligible schemes" },
    { key: "documents", label: "Document Agent", icon: "📄", desc: "Validating documents" },
    { key: "adversarial", label: "Adversarial Agent", icon: "🛡️", desc: "Predicting rejection risk" },
    { key: "execution", label: "Execution Agent", icon: "⚡", desc: "Submitting application" },
];

export default function PipelinePage() {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeStage, setActiveStage] = useState(-1);
    const [formData, setFormData] = useState({
        name: "Lakshmi Devi",
        age: 41,
        gender: "female",
        annual_income: 180000,
        occupation: "farmer",
        education: "secondary",
        is_bpl: true,
        caste_category: "obc",
        state: "Uttar Pradesh",
        city: "Varanasi",
        aadhaar_number: "1234-5678-9012",
        bank_account: "ACC12345678",
        bank_ifsc: "SBIN0001234",
        is_pregnant: false,
        is_disabled: false,
        is_minority: false,
        documents: "aadhaar,income_certificate,bank_statement,caste_certificate,bpl_card",
        scheme_id: "pm_kisan",
    });

    const updateField = (k, v) => setFormData((prev) => ({ ...prev, [k]: v }));

    const runPipeline = async () => {
        setLoading(true);
        setResult(null);

        // Animate stages
        for (let i = 0; i < STAGES.length; i++) {
            setActiveStage(i);
            await new Promise((r) => setTimeout(r, 600));
        }

        try {
            const body = {
                profile: {
                    name: formData.name,
                    age: parseInt(formData.age),
                    gender: formData.gender,
                    annual_income: parseFloat(formData.annual_income),
                    occupation: formData.occupation,
                    education: formData.education,
                    is_bpl: formData.is_bpl,
                    is_pregnant: formData.is_pregnant,
                    is_disabled: formData.is_disabled,
                    is_minority: formData.is_minority,
                    caste_category: formData.caste_category,
                    aadhaar_number: formData.aadhaar_number,
                    bank_account: formData.bank_account,
                    bank_ifsc: formData.bank_ifsc,
                    address: { city: formData.city, state: formData.state },
                    documents: formData.documents.split(",").map((d) => d.trim()),
                    consent_retention: true,
                },
                scheme_id: formData.scheme_id,
            };

            const r = await fetch(`${API}/api/agents/pipeline`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const data = await r.json();
            setResult(data);
            setActiveStage(STAGES.length);
        } catch {
            alert("Backend not running. Start: python -m uvicorn backend.main:app --port 8000");
        }
        setLoading(false);
    };

    const riskLevel = result?.rejection_analysis?.risk_level || "low";
    const riskProb = result?.rejection_analysis?.rejection_probability || 0;
    const app = result?.application || {};

    return (
        <main className="container">
            <div className="page-header">
                <h1>🚀 AI Pipeline</h1>
                <p>Run the full multi-agent pipeline — profile → eligibility → documents → risk → submission</p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 24, alignItems: "start" }}>
                {/* Left: Form + Results */}
                <div>
                    <div className="card" style={{ marginBottom: 24 }}>
                        <h3 style={{ marginBottom: 16 }}>Citizen Profile</h3>
                        <div className="form-grid">
                            <div className="input-group">
                                <label>Full Name</label>
                                <input className="input" value={formData.name} onChange={(e) => updateField("name", e.target.value)} />
                            </div>
                            <div className="input-group">
                                <label>Age</label>
                                <input className="input" type="number" value={formData.age} onChange={(e) => updateField("age", e.target.value)} />
                            </div>
                            <div className="input-group">
                                <label>Gender</label>
                                <select className="select" value={formData.gender} onChange={(e) => updateField("gender", e.target.value)}>
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                            <div className="input-group">
                                <label>Annual Income (₹)</label>
                                <input className="input" type="number" value={formData.annual_income} onChange={(e) => updateField("annual_income", e.target.value)} />
                            </div>
                            <div className="input-group">
                                <label>Occupation</label>
                                <select className="select" value={formData.occupation} onChange={(e) => updateField("occupation", e.target.value)}>
                                    {["farmer", "daily_wage", "self_employed", "salaried", "student", "homemaker", "unemployed", "retired", "other"].map(o => (
                                        <option key={o} value={o}>{o.replace(/_/g, " ")}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="input-group">
                                <label>Education</label>
                                <select className="select" value={formData.education} onChange={(e) => updateField("education", e.target.value)}>
                                    {["none", "primary", "secondary", "higher_secondary", "graduate", "post_graduate", "doctorate"].map(e => (
                                        <option key={e} value={e}>{e.replace(/_/g, " ")}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="input-group">
                                <label>Caste Category</label>
                                <select className="select" value={formData.caste_category} onChange={(e) => updateField("caste_category", e.target.value)}>
                                    {["general", "obc", "sc", "st", "ews"].map(c => (
                                        <option key={c} value={c}>{c.toUpperCase()}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="input-group">
                                <label>State</label>
                                <input className="input" value={formData.state} onChange={(e) => updateField("state", e.target.value)} />
                            </div>
                            <div className="input-group">
                                <label>Aadhaar Number</label>
                                <input className="input" value={formData.aadhaar_number} onChange={(e) => updateField("aadhaar_number", e.target.value)} />
                            </div>
                            <div className="input-group">
                                <label>Target Scheme</label>
                                <select className="select" value={formData.scheme_id} onChange={(e) => updateField("scheme_id", e.target.value)}>
                                    {["pm_kisan", "pmay", "pm_ujjwala", "ayushman_bharat", "nfsa_ration", "pm_jan_dhan", "atal_pension", "national_scholarship", "mudra_loan", "pm_fasal_bima", "standup_india"].map(s => (
                                        <option key={s} value={s}>{s.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", margin: "16px 0" }}>
                            {[{ k: "is_bpl", l: "BPL" }, { k: "is_pregnant", l: "Pregnant" }, { k: "is_disabled", l: "Disabled" }, { k: "is_minority", l: "Minority" }].map(cb => (
                                <label key={cb.k} className="checkbox-group">
                                    <input type="checkbox" checked={formData[cb.k]} onChange={(e) => updateField(cb.k, e.target.checked)} />
                                    {cb.l}
                                </label>
                            ))}
                        </div>

                        <div className="input-group" style={{ marginBottom: 16 }}>
                            <label>Documents (comma-separated)</label>
                            <input className="input" value={formData.documents} onChange={(e) => updateField("documents", e.target.value)} />
                        </div>

                        <button className="btn btn-primary btn-lg" onClick={runPipeline} disabled={loading} style={{ width: "100%" }}>
                            {loading ? <><span className="spinner" style={{ width: 18, height: 18 }}></span> Running Pipeline...</> : "🚀 Execute Full Pipeline"}
                        </button>
                    </div>

                    {/* Results */}
                    {result && (
                        <div className="animate-fade-in">
                            {/* Eligible Schemes Summary */}
                            {result.eligible_schemes?.length > 0 && (
                                <div className="card" style={{ marginBottom: 16 }}>
                                    <h3 style={{ marginBottom: 12 }}>
                                        🎯 Eligible Schemes ({result.eligible_schemes.filter(s => s.is_eligible).length})
                                    </h3>
                                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                        {result.eligible_schemes.filter(s => s.is_eligible).slice(0, 5).map((s) => (
                                            <div key={s.scheme_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", background: "var(--bg-input)", borderRadius: "var(--radius-sm)" }}>
                                                <div>
                                                    <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{s.scheme_name}</div>
                                                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                                                        Rank #{s.rank} • {(s.approval_probability * 100).toFixed(0)}% approval
                                                    </div>
                                                </div>
                                                <div style={{ fontWeight: 700, color: "var(--accent-green)" }}>
                                                    ₹{s.benefit_amount.toLocaleString()}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Application Result */}
                            {app.application_id && (
                                <div className="card" style={{ marginBottom: 16 }}>
                                    <h3 style={{ marginBottom: 12 }}>📋 Application Submitted</h3>
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                                        {[
                                            ["Application ID", app.application_id],
                                            ["Status", app.status],
                                            ["Confirmation", app.confirmation_number || "Pending"],
                                            ["Scheme", app.scheme_name],
                                            ["Tier", `Tier ${app.execution_tier}`],
                                            ["Benefit", `₹${app.benefit_amount?.toLocaleString()}`],
                                        ].map(([label, val]) => (
                                            <div key={label} style={{ padding: "8px 12px", background: "var(--bg-input)", borderRadius: "var(--radius-sm)" }}>
                                                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{label}</div>
                                                <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{val}</div>
                                            </div>
                                        ))}
                                    </div>
                                    {app.status === "submitted" && (
                                        <div className="alert alert-success" style={{ marginTop: 12 }}>
                                            ✅ Application submitted successfully! Confirmation: {app.confirmation_number}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Right: Pipeline Visualization */}
                <div style={{ position: "sticky", top: 90 }}>
                    <div className="card">
                        <h3 style={{ marginBottom: 16 }}>Pipeline Status</h3>
                        <div className="pipeline-steps">
                            {STAGES.map((stage, i) => {
                                let status = "pending";
                                if (i < activeStage) status = "complete";
                                else if (i === activeStage && loading) status = "active";
                                else if (result && i <= STAGES.length - 1) status = "complete";

                                const event = result?.events?.find((e) => e.stage === stage.key);

                                return (
                                    <div key={stage.key} className={`pipeline-step ${status}`}>
                                        <div className={`pipeline-icon ${status}`}>
                                            {status === "complete" ? "✓" : status === "active" ? (
                                                <span className="spinner" style={{ width: 18, height: 18 }}></span>
                                            ) : stage.icon}
                                        </div>
                                        <div className="pipeline-info">
                                            <h4>{stage.label}</h4>
                                            <p>{event?.message || stage.desc}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Risk Gauge */}
                    {result?.rejection_analysis && (
                        <div className="card animate-fade-in" style={{ marginTop: 16 }}>
                            <h3 style={{ marginBottom: 16, textAlign: "center" }}>Rejection Risk</h3>
                            <div className="risk-gauge">
                                <div className={`risk-circle risk-${riskLevel === "critical" ? "high" : riskLevel}`}>
                                    {(riskProb * 100).toFixed(0)}%
                                </div>
                                <span className={`badge badge-${riskLevel === "low" ? "green" : riskLevel === "medium" ? "yellow" : "red"}`}>
                                    {riskLevel.toUpperCase()} RISK
                                </span>
                            </div>
                            {result.rejection_analysis.recommendations?.length > 0 && (
                                <div style={{ marginTop: 16 }}>
                                    <div style={{ fontSize: "0.8125rem", fontWeight: 600, marginBottom: 8 }}>Recommendations</div>
                                    {result.rejection_analysis.recommendations.map((r, i) => (
                                        <div key={i} style={{ fontSize: "0.8125rem", color: "var(--text-secondary)", padding: "4px 0" }}>
                                            • {r}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
