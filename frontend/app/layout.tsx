import type { Metadata } from "next";
import { Space_Grotesk } from "next/font/google";
import "./globals.css";

const space = Space_Grotesk({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Fact Archiver",
  description: "Evidence ledger for claims, artifacts, and transparency logs.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "";
  const verificationHref = apiBase
    ? `${apiBase.replace(/\/$/, "")}/verification`
    : "/verification";

  return (
    <html lang="en" className={space.className}>
      <body>
        <div className="app">
          <header className="site-header">
            <div className="brand">
              <span className="brand-dot" />
              <div>
                <strong>Fact Archiver</strong>
                <span>Evidence Ledger</span>
              </div>
            </div>
            <nav className="nav">
              <a href="/">Home</a>
              <a href="/review">Review Queue</a>
              <a href={verificationHref}>Verification</a>
            </nav>
          </header>
          <main className="main">{children}</main>
        </div>
      </body>
    </html>
  );
}
