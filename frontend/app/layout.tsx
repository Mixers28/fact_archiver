import type { Metadata } from "next";
import { Space_Grotesk } from "next/font/google";
import "./globals.css";

const space = Space_Grotesk({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Fact Archiver",
  description: "Evidence ledger for claims, artifacts, and transparency logs.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={space.className}>
      <body>
        <div className="app">{children}</div>
      </body>
    </html>
  );
}
