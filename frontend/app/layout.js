import "./globals.css";

export const metadata = {
  title: "BharatBridge — AI Agent for Public Infrastructure",
  description:
    "Multi-agent AI system automating citizen access to government welfare, scholarships, and subsidies. Powered by graph reasoning, document intelligence, and adversarial validation.",
};

import { AccessibilityProvider } from "./context/AccessibilityContext";
import Link from "next/link";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AccessibilityProvider>
          <nav className="nav">
            <div className="container nav-inner">
              <Link href="/" className="nav-brand">
                🏛️ <span>BharatBridge</span>
              </Link>
              <div className="nav-links">
                <Link href="/" className="nav-link">Home</Link>
                <Link href="/discover" className="nav-link">Discover</Link>
                <Link href="/pipeline" className="nav-link">Pipeline</Link>
                <Link href="/tracking" className="nav-link">Tracking</Link>
                <Link href="/accessibility" className="nav-link">Accessibility</Link>
                <Link href="/settings" className="nav-link">Settings</Link>
              </div>
            </div>
          </nav>
          {children}
        </AccessibilityProvider>
      </body>
    </html>
  );
}
