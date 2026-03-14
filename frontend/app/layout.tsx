// app/layout.tsx — The root layout wraps every page.
// Think of it as the outer shell: sidebar + main content area.
// Next.js renders this around every page automatically.

import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "./components/Sidebar";

export const metadata: Metadata = {
  title: "AstraShield — AI Fraud Detection",
  description: "AI-Powered Deepfake & Identity Fraud Detection Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {/* Animated background grid */}
        <div className="fixed inset-0 bg-grid opacity-30 pointer-events-none z-0" />

        {/* Corner decorations */}
        <div className="fixed top-0 left-0 w-32 h-32 pointer-events-none z-0"
          style={{ background: "radial-gradient(circle at top left, rgba(13,148,136,0.12) 0%, transparent 70%)" }}
        />
        <div className="fixed bottom-0 right-0 w-48 h-48 pointer-events-none z-0"
          style={{ background: "radial-gradient(circle at bottom right, rgba(13,148,136,0.08) 0%, transparent 70%)" }}
        />

        {/* Main app layout: sidebar + content */}
        <div className="relative z-10 flex min-h-screen">
          <Sidebar />
          <main className="flex-1 ml-64 p-8 overflow-y-auto min-h-screen">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
