"use client";
import { useState } from "react";

const API = "http://127.0.0.1:8000";

export default function TrackingPage() {
    const [appId, setAppId] = useState("");
    const [app, setApp] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const trackApplication = async () => {
        if (!appId.trim()) return;
        setLoading(true);
        setError("");
        try {
            const r = await fetch(`${API}/api/applications/${appId}`);
            if (!r.ok) throw new Error("Application not found");
            const d = await r.json();
            setApp(d.application);
        } catch (e) {
            setError(e.message || "Not found");
            setApp(null);
        }
        setLoading(false);
    };

    const statusColors = {
        draft: "yellow",
        submitted: "blue",
        under_review: "purple",
        approved: "green",
        rejected: "red",
        appealed: "orange",
    };

    return (
        <main className="container">
            <div className="page-header">
                <h1>📊 Application Tracking</h1>
                <p>Track your application status in real-time</p>
            </div>

            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ display: "flex", gap: 12 }}>
                    <input
                        className="input"
                        style={{ flex: 1 }}
                        placeholder="Enter Application ID (e.g., APP-XXXXXXXX)"
                        value={appId}
                        onChange={(e) => setAppId(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && trackApplication()}
                    />
                    <button className="btn btn-primary" onClick={trackApplication} disabled={loading}>
                        {loading ? <span className="spinner" style={{ width: 16, height: 16 }}></span> : "Track"}
                    </button>
                </div>
                {error && <div className="alert alert-error" style={{ marginTop: 12 }}>❌ {error}</div>}
            </div>

            {app && (
                <div className="animate-fade-in">
                    <div className="card" style={{ marginBottom: 20 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                            <h2 style={{ fontSize: "1.25rem" }}>{app.scheme_name}</h2>
                            <span className={`badge badge-${statusColors[app.status] || "blue"}`}>
                                {app.status?.replace(/_/g, " ").toUpperCase()}
                            </span>
                        </div>

                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
                            {[
                                ["Application ID", app.application_id],
                                ["Citizen ID", app.citizen_id],
                                ["Submission Date", app.submission_date ? new Date(app.submission_date).toLocaleDateString() : "N/A"],
                                ["Confirmation", app.confirmation_number || "Pending"],
                                ["Expected Decision", app.expected_decision_date ? new Date(app.expected_decision_date).toLocaleDateString() : "N/A"],
                                ["Benefit Amount", `₹${(app.benefit_amount || 0).toLocaleString()}`],
                                ["Execution Tier", `Tier ${app.execution_tier}`],
                                ["Portal", app.portal_url || "N/A"],
                            ].map(([label, val]) => (
                                <div key={label} style={{ padding: "10px 14px", background: "var(--bg-input)", borderRadius: "var(--radius-sm)" }}>
                                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 2 }}>{label}</div>
                                    <div style={{ fontWeight: 600, fontSize: "0.875rem", wordBreak: "break-all" }}>{val}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Status Timeline */}
                    <div className="card" style={{ marginBottom: 20 }}>
                        <h3 style={{ marginBottom: 16 }}>Status Timeline</h3>
                        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
                            {["draft", "submitted", "under_review", app.status === "approved" ? "approved" : app.status === "rejected" ? "rejected" : "pending"].map((stage, i) => {
                                const isActive = stage === app.status;
                                const isPast = ["draft", "submitted", "under_review", "approved", "rejected"].indexOf(app.status) >= i;
                                const icons = { draft: "📝", submitted: "📤", under_review: "🔍", approved: "✅", rejected: "❌", pending: "⏳" };

                                return (
                                    <div key={stage} style={{ display: "flex", gap: 16 }}>
                                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                                            <div style={{
                                                width: 36, height: 36, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                                                background: isPast ? "rgba(45,212,168,0.2)" : "var(--bg-input)",
                                                border: isActive ? "2px solid var(--accent-green)" : "2px solid var(--border)",
                                                fontSize: "1rem",
                                            }}>
                                                {icons[stage]}
                                            </div>
                                            {i < 3 && <div style={{ width: 2, height: 32, background: isPast ? "var(--accent-green)" : "var(--border)" }}></div>}
                                        </div>
                                        <div style={{ paddingBottom: 16 }}>
                                            <div style={{ fontWeight: 600, fontSize: "0.875rem", color: isPast ? "var(--text-primary)" : "var(--text-muted)" }}>
                                                {stage.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
                                            </div>
                                            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                                                {isActive ? "Current stage" : isPast ? "Completed" : "Upcoming"}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Audit Trail */}
                    {app.audit_trail?.length > 0 && (
                        <div className="card">
                            <h3 style={{ marginBottom: 16 }}>Audit Trail</h3>
                            {app.audit_trail.map((entry, i) => (
                                <div key={i} style={{ padding: "10px 14px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{entry.action}</div>
                                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{entry.details}</div>
                                    </div>
                                    <span className={`badge ${entry.success ? "badge-green" : "badge-red"}`}>
                                        {entry.success ? "✓" : "✗"}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {!app && !error && (
                <div className="empty-state">
                    <div className="icon">📊</div>
                    <p style={{ marginBottom: 8 }}>Enter an application ID to track its status</p>
                    <p style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>
                        Run the pipeline first to get an application ID, then track it here
                    </p>
                </div>
            )}
        </main>
    );
}
