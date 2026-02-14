"use client";
import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000";

export default function DiscoverPage() {
    const [schemes, setSchemes] = useState([]);
    const [matches, setMatches] = useState(null);
    const [loading, setLoading] = useState(false);
    const [tab, setTab] = useState("all");

    // Demo profile for quick discovery
    const demoProfile = {
        name: "Lakshmi Devi",
        age: 41,
        gender: "female",
        annual_income: 180000,
        occupation: "farmer",
        education: "secondary",
        is_bpl: true,
        caste_category: "obc",
        address: { city: "Varanasi", state: "Uttar Pradesh" },
        bank_account: "ACC12345678",
        aadhaar_number: "1234-5678-9012",
        documents: ["aadhaar", "income_certificate", "bank_statement", "caste_certificate", "bpl_card"],
    };

    useEffect(() => {
        fetch(`${API}/api/schemes/`)
            .then((r) => r.json())
            .then((d) => setSchemes(d.schemes || []))
            .catch(() => { });
    }, []);

    const discoverSchemes = async () => {
        setLoading(true);
        try {
            const r = await fetch(`${API}/api/schemes/discover`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(demoProfile),
            });
            const d = await r.json();
            setMatches(d);
            setTab("eligible");
        } catch {
            alert("Backend not running. Start it with: python -m uvicorn backend.main:app --port 8000");
        }
        setLoading(false);
    };

    const eligible = matches?.matches?.filter((m) => m.is_eligible) || [];
    const notEligible = matches?.matches?.filter((m) => !m.is_eligible) || [];

    return (
        <main className="container">
            <div className="page-header">
                <h1>🔍 Scheme Discovery</h1>
                <p>
                    Find government schemes you're eligible for using AI-powered graph
                    reasoning
                </p>
            </div>

            {/* Demo Profile Card */}
            <div className="card card-glow" style={{ marginBottom: 24 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
                    <div>
                        <h3 style={{ marginBottom: 4 }}>Demo Citizen Profile</h3>
                        <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
                            {demoProfile.name} • {demoProfile.age}yo {demoProfile.gender} •{" "}
                            {demoProfile.occupation} • ₹{demoProfile.annual_income.toLocaleString()}/yr •{" "}
                            {demoProfile.caste_category.toUpperCase()} • BPL
                        </p>
                    </div>
                    <button
                        className="btn btn-primary"
                        onClick={discoverSchemes}
                        disabled={loading}
                    >
                        {loading ? (
                            <><span className="spinner" style={{ width: 16, height: 16 }}></span> Discovering...</>
                        ) : (
                            "🎯 Discover Eligible Schemes"
                        )}
                    </button>
                </div>
            </div>

            {/* Results */}
            {matches && (
                <div className="results-panel animate-fade-in">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                        <h2>
                            Found {eligible.length} Eligible Schemes{" "}
                            <span style={{ color: "var(--text-muted)", fontWeight: 400, fontSize: "1rem" }}>
                                out of {matches.total_schemes}
                            </span>
                        </h2>
                        <div className="tabs">
                            <button className={`tab ${tab === "eligible" ? "active" : ""}`} onClick={() => setTab("eligible")}>
                                Eligible ({eligible.length})
                            </button>
                            <button className={`tab ${tab === "all" ? "active" : ""}`} onClick={() => setTab("all")}>
                                All ({matches.total_schemes})
                            </button>
                        </div>
                    </div>

                    <div className="grid-2">
                        {(tab === "eligible" ? eligible : matches.matches).map((m) => (
                            <div key={m.scheme.scheme_id} className="card scheme-card animate-fade-in-up" style={{ opacity: 1 }}>
                                <div className="scheme-header">
                                    <div>
                                        <h3>{m.scheme.name}</h3>
                                        <div className="scheme-ministry">{m.scheme.ministry}</div>
                                    </div>
                                    <span className={`badge ${m.is_eligible ? "badge-green" : "badge-red"}`}>
                                        {m.is_eligible ? "✓ Eligible" : "✗ Not Eligible"}
                                    </span>
                                </div>

                                <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>
                                    {m.scheme.description}
                                </p>

                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                    <div className="scheme-benefit">₹{m.estimated_benefit.toLocaleString()}</div>
                                    <div style={{ textAlign: "right" }}>
                                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Approval Probability</div>
                                        <div style={{ fontWeight: 700, color: m.approval_probability > 0.6 ? "var(--accent-green)" : "var(--accent-yellow)" }}>
                                            {(m.approval_probability * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                </div>

                                <div className="progress-bar">
                                    <div
                                        className={`progress-fill ${m.eligibility_score >= 0.8 ? "progress-green" : m.eligibility_score >= 0.5 ? "progress-yellow" : "progress-red"}`}
                                        style={{ width: `${m.eligibility_score * 100}%` }}
                                    ></div>
                                </div>

                                {m.missing_documents.length > 0 && (
                                    <div className="alert alert-warning" style={{ fontSize: "0.8125rem" }}>
                                        ⚠ Missing: {m.missing_documents.join(", ").replace(/_/g, " ")}
                                    </div>
                                )}

                                {m.conflicts.length > 0 && (
                                    <div className="alert alert-error" style={{ fontSize: "0.8125rem" }}>
                                        ⚡ Conflicts with: {m.conflicts.join(", ")}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* All Schemes (before discovery) */}
            {!matches && schemes.length > 0 && (
                <div>
                    <h2 style={{ marginBottom: 20 }}>
                        All Available Schemes ({schemes.length})
                    </h2>
                    <div className="grid-2">
                        {schemes.map((s) => (
                            <div key={s.scheme_id} className="card scheme-card">
                                <div className="scheme-header">
                                    <h3>{s.name}</h3>
                                    <span className={`badge badge-${s.category === "agriculture" ? "green" : s.category === "healthcare" ? "blue" : s.category === "scholarship" ? "purple" : "orange"}`}>
                                        {s.category.replace(/_/g, " ")}
                                    </span>
                                </div>
                                <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>
                                    {s.description}
                                </p>
                                <div className="scheme-benefit">₹{s.benefit_amount.toLocaleString()}</div>
                                <div className="scheme-ministry">{s.ministry}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!matches && schemes.length === 0 && (
                <div className="empty-state">
                    <div className="icon">🔌</div>
                    <p>Start the backend to load schemes</p>
                    <code style={{ color: "var(--accent-orange)", fontSize: "0.875rem" }}>
                        python -m uvicorn backend.main:app --port 8000
                    </code>
                </div>
            )}
        </main>
    );
}
