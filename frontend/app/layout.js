import "./globals.css";

export const metadata = {
  title: "BharatBridge — AI Agent for Public Infrastructure",
  description:
    "Multi-agent AI system automating citizen access to government welfare, scholarships, and subsidies. Powered by graph reasoning, document intelligence, and adversarial validation.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="container nav-inner">
            <a href="/" className="nav-brand">
              🏛️ <span>BharatBridge</span>
            </a>
            <div className="nav-links">
              <a href="/" className="nav-link">Home</a>
              <a href="/discover" className="nav-link">Discover</a>
              <a href="/pipeline" className="nav-link">Pipeline</a>
              <a href="/tracking" className="nav-link">Tracking</a>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
