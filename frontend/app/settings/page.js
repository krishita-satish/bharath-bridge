"use client";
import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000";

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState("about");
    const [schemes, setSchemes] = useState([]);
    const [loadingSchemes, setLoadingSchemes] = useState(false);

    // Mock Applications Data (In real app, fetch from DB based on user)
    const [myApplications, setMyApplications] = useState([
        { id: "APP-2024-001", scheme: "PM Kisan Samman Nidhi", status: "approved", date: "2024-01-15" },
        { id: "APP-2024-045", scheme: "Ayushman Bharat", status: "pending", date: "2024-02-10" },
        { id: "APP-2023-892", scheme: "Post Matric Scholarship", status: "rejected", date: "2023-11-20" }
    ]);


    useEffect(() => {
        if (activeTab === "schemes" && schemes.length === 0) {
            setLoadingSchemes(true);
            fetch(`${API}/api/schemes/`)
                .then((r) => r.json())
                .then((d) => setSchemes(d.schemes || []))
                .catch(() => { })
                .finally(() => setLoadingSchemes(false));
        }
    }, [activeTab]);

    return (
        <main className="container">
            <div className="page-header">
                <h1>⚙️ Settings</h1>
                <p>Manage your preferences and view application history.</p>
            </div>

            <div className="settings-layout">
                {/* Sidebar Navigation */}
                <div className="settings-sidebar card">
                    <button
                        className={`sidebar-item ${activeTab === "about" ? "active" : ""}`}
                        onClick={() => setActiveTab("about")}
                    >
                        ℹ️ About BharatBridge
                    </button>
                    <button
                        className={`sidebar-item ${activeTab === "schemes" ? "active" : ""}`}
                        onClick={() => setActiveTab("schemes")}
                    >
                        📜 Schemes & Details
                    </button>
                    <button
                        className={`sidebar-item ${activeTab === "applications" ? "active" : ""}`}
                        onClick={() => setActiveTab("applications")}
                    >
                        📂 My Applications
                    </button>
                </div>

                {/* Content Area */}
                <div className="settings-content">

                    {/* 1. ABOUT SECTION */}
                    {activeTab === "about" && (
                        <div className="card animate-fade-in">
                            <h2 className="section-title-sm">About BharatBridge</h2>
                            <p className="text-secondary mb-4">
                                BharatBridge is an AI-driven public infrastructure agent designed to democratize access to government welfare.
                            </p>

                            <div className="mission-box">
                                <h3>Our Mission</h3>
                                <p>
                                    To eliminate the barriers of discovery, comprehension, and process complexity that prevent citizens from accessing their rightful government benefits.
                                    By leveraging multi-agent AI, knowledge graphs, and document intelligence, we aim to reduce rejection rates and ensure 100% coverage for eligible citizens.
                                </p>
                            </div>

                            <div className="info-grid">
                                <div className="info-item">
                                    <h4>Version</h4>
                                    <p>1.0.0 (Beta)</p>
                                </div>
                                <div className="info-item">
                                    <h4>Developer</h4>
                                    <p>Google DeepMind Team</p>
                                </div>
                                <div className="info-item">
                                    <h4>Support</h4>
                                    <p>support@bharatbridge.gov.in</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 2. SCHEMES SECTION */}
                    {activeTab === "schemes" && (
                        <div className="animate-fade-in">
                            <h2 className="section-title-sm mb-4">Available Government Schemes</h2>

                            {loadingSchemes && <div className="spinner center-spinner"></div>}

                            {!loadingSchemes && schemes.length === 0 && (
                                <div className="alert alert-warning">
                                    No schemes loaded. Ensure backend is running.
                                </div>
                            )}

                            <div className="schemes-list">
                                {schemes.map((s) => (
                                    <div key={s.scheme_id} className="card scheme-list-item">
                                        <div className="scheme-info">
                                            <h3>{s.name}</h3>
                                            <p className="text-sm text-secondary">{s.description}</p>
                                            <div className="tags">
                                                <span className="badge badge-blue">{s.ministry}</span>
                                                <span className="badge badge-green">Benefit: ₹{s.benefit_amount.toLocaleString()}</span>
                                            </div>
                                        </div>
                                        <button className="btn btn-sm btn-secondary">View Details</button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 3. MY APPLICATIONS SECTION */}
                    {activeTab === "applications" && (
                        <div className="animate-fade-in">
                            <h2 className="section-title-sm mb-4">My Applications</h2>

                            <div className="applications-list">
                                {myApplications.map((app) => (
                                    <div key={app.id} className="card app-item">
                                        <div className="app-header">
                                            <span className="app-id">{app.id}</span>
                                            <span className={`badge badge-${app.status === 'approved' ? 'green' :
                                                    app.status === 'rejected' ? 'red' : 'yellow'
                                                }`}>
                                                {app.status.toUpperCase()}
                                            </span>
                                        </div>
                                        <h3>{app.scheme}</h3>
                                        <p className="text-sm text-secondary">Submitted on: {new Date(app.date).toLocaleDateString()}</p>
                                        <button className="btn btn-sm btn-ghost mt-2">View Full Details</button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                </div>
            </div>

            <style jsx>{`
                .settings-layout {
                    display: grid;
                    grid-template-columns: 250px 1fr;
                    gap: 24px;
                    align-items: start;
                }

                .settings-sidebar {
                    padding: 12px;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .sidebar-item {
                    text-align: left;
                    padding: 12px 16px;
                    background: transparent;
                    border: none;
                    color: var(--text-secondary);
                    font-weight: 500;
                    cursor: pointer;
                    border-radius: var(--radius-sm);
                    transition: all 0.2s;
                }

                .sidebar-item:hover {
                    background: var(--bg-primary);
                    color: var(--text-primary);
                }

                .sidebar-item.active {
                    background: var(--bg-primary);
                    color: var(--accent-orange);
                    font-weight: 600;
                    border-left: 3px solid var(--accent-orange);
                }

                .section-title-sm {
                    font-size: 1.25rem;
                    font-weight: 700;
                    margin-bottom: 16px;
                }

                .mission-box {
                    background: var(--bg-primary);
                    padding: 16px;
                    border-radius: var(--radius-md);
                    border-left: 4px solid var(--accent-blue);
                    margin-bottom: 24px;
                }

                .mission-box h3 {
                    font-size: 1rem;
                    margin-bottom: 8px;
                    color: var(--accent-blue);
                }

                .mission-box p {
                    font-size: 0.9rem;
                    line-height: 1.6;
                    color: var(--text-secondary);
                }

                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 16px;
                }

                .info-item h4 {
                    font-size: 0.8rem;
                    color: var(--text-muted);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }

                .schemes-list, .applications-list {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }

                .scheme-list-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 16px;
                }

                .scheme-info h3 {
                    font-size: 1rem;
                    margin-bottom: 4px;
                }

                .tags {
                    display: flex;
                    gap: 8px;
                    margin-top: 8px;
                }

                .app-item {
                    padding: 16px;
                }

                .app-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }

                .app-id {
                    font-family: monospace;
                    font-size: 0.85rem;
                    color: var(--text-muted);
                }

                .text-secondary { color: var(--text-secondary); }
                .text-sm { font-size: 0.875rem; }
                .mb-4 { margin-bottom: 16px; }
                .mt-2 { margin-top: 8px; }
                .center-spinner { margin: 40px auto; }

                @media (max-width: 768px) {
                    .settings-layout {
                        grid-template-columns: 1fr;
                    }
                    .settings-sidebar {
                        flex-direction: row;
                        overflow-x: auto;
                        padding-bottom: 12px;
                    }
                    .sidebar-item {
                        white-space: nowrap;
                    }
                }
            `}</style>
        </main>
    );
}
