"use client";
import Link from "next/link";

export default function Home() {
  return (
    <main>
      {/* ── Hero Section ────────────────────────────────────────── */}
      <section className="hero">
        <div className="hero-badge animate-fade-in-up">
          🤖 Multi-Agent AI × Knowledge Graph × Adversarial Validation
        </div>

        <h1 className="animate-fade-in-up delay-1">
          From <span className="gradient-text">Barrier</span> to{" "}
          <span className="gradient-text">Bridge</span>
        </h1>

        <p className="animate-fade-in-up delay-2">
          BharatBridge is an AI Execution Agent that automates citizen access to
          government welfare, scholarships, and subsidies — defeating discovery,
          comprehension, process, and execution barriers.
        </p>

        <div className="hero-actions animate-fade-in-up delay-3">
          <Link href="/pipeline" className="btn btn-primary btn-lg">
            🚀 Run AI Pipeline
          </Link>
          <Link href="/discover" className="btn btn-secondary btn-lg">
            🔍 Discover Schemes
          </Link>
        </div>

        <div className="stats-grid animate-fade-in-up delay-4">
          <div className="stat-card">
            <div className="stat-value">5,000+</div>
            <div className="stat-label">Government Schemes</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">73%</div>
            <div className="stat-label">Application Rejection Rate</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">90s</div>
            <div className="stat-label">Average Pipeline Time</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">6</div>
            <div className="stat-label">Specialized AI Agents</div>
          </div>
        </div>
      </section>

      {/* ── How It Works ────────────────────────────────────────── */}
      <section className="section" style={{ background: "var(--bg-secondary)" }}>
        <div className="container">
          <div className="section-title">
            <h2>How BharatBridge Works</h2>
            <p>
              Six specialized AI agents working together to get you your rightful
              benefits
            </p>
          </div>

          <div className="steps-grid">
            {[
              {
                num: 1,
                title: "Profiler Agent",
                desc: "Extracts your profile from Aadhaar, income certificates, and other documents using AI-powered OCR.",
                icon: "👤",
              },
              {
                num: 2,
                title: "Eligibility Agent",
                desc: "Uses knowledge graph with 16+ schemes to find every benefit you qualify for, ranked by impact.",
                icon: "🎯",
              },
              {
                num: 3,
                title: "Document Agent",
                desc: "Validates all your documents, checks authenticity, flags issues, and redacts PII automatically.",
                icon: "📄",
              },
              {
                num: 4,
                title: "Adversarial Agent",
                desc: "Predicts rejection probability, identifies risk factors, and tells you exactly how to fix them.",
                icon: "🛡️",
              },
              {
                num: 5,
                title: "Execution Agent",
                desc: "Auto-fills and submits your application via API, web automation, or generates pre-filled PDFs.",
                icon: "⚡",
              },
              {
                num: 6,
                title: "Appeals Agent",
                desc: "If rejected, generates formal appeal letters with legal precedents in English or Hindi.",
                icon: "⚖️",
              },
            ].map((step) => (
              <div
                key={step.num}
                className="card step-card animate-fade-in-up"
                style={{ animationDelay: `${step.num * 0.1}s`, opacity: 0 }}
              >
                <div className="step-number">{step.num}</div>
                <div style={{ fontSize: "2rem", marginBottom: 8 }}>
                  {step.icon}
                </div>
                <h3>{step.title}</h3>
                <p>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Architecture ────────────────────────────────────────── */}
      <section className="section">
        <div className="container">
          <div className="section-title">
            <h2>Architecture at a Glance</h2>
            <p>Production-ready design built on AWS services</p>
          </div>

          <div className="grid-3">
            {[
              {
                title: "Knowledge Graph",
                desc: "NetworkX graph (Neptune-ready) with 16 schemes, 34 rules, 92 edges. Multi-hop traversal up to 5 hops for cascade benefits.",
                badge: "Neptune",
                color: "blue",
              },
              {
                title: "Document Intelligence",
                desc: "Simulated Textract pipeline supporting 13 document types with OCR extraction, authenticity validation, and PII redaction.",
                badge: "Textract",
                color: "purple",
              },
              {
                title: "Rejection Prediction",
                desc: "Hybrid model combining rule-based analysis with simulated XGBoost (SageMaker-ready) for rejection probability estimation.",
                badge: "SageMaker",
                color: "green",
              },
              {
                title: "Multi-Agent Orchestrator",
                desc: "Step Functions-simulated pipeline coordinating 6 agents with state persistence, retry logic, and event emission.",
                badge: "Step Functions",
                color: "orange",
              },
              {
                title: "3-Tier Execution",
                desc: "API submission → Web automation → PDF generation fallback with exponential backoff retry (1s, 2s, 4s).",
                badge: "Lambda",
                color: "yellow",
              },
              {
                title: "Security & Privacy",
                desc: "PII redaction in all logs, Aadhaar encryption markers, consent-based retention, GDPR-compliant data deletion.",
                badge: "KMS",
                color: "red",
              },
            ].map((item) => (
              <div key={item.title} className="card card-glow">
                <span className={`badge badge-${item.color}`} style={{ marginBottom: 12 }}>
                  {item.badge}
                </span>
                <h3 style={{ marginBottom: 8, fontSize: "1.0625rem" }}>{item.title}</h3>
                <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────── */}
      <section
        className="section"
        style={{
          background: "var(--bg-secondary)",
          textAlign: "center",
          paddingBottom: 60,
        }}
      >
        <div className="container">
          <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: 12 }}>
            Ready to claim your <span className="gradient-text" style={{
              background: "var(--gradient-hero)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text"
            }}>rightful benefits</span>?
          </h2>
          <p
            style={{
              color: "var(--text-secondary)",
              maxWidth: 500,
              margin: "0 auto 24px",
            }}
          >
            Run the full AI pipeline now — profile extraction, scheme discovery,
            document validation, risk analysis, and automated submission in one go.
          </p>
          <Link href="/pipeline" className="btn btn-primary btn-lg">
            🚀 Start Pipeline
          </Link>
        </div>
      </section>
    </main>
  );
}
