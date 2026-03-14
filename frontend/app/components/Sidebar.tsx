// app/components/Sidebar.tsx — The left navigation bar.
// Shows the AstraShield logo and links to all pages.
// "use client" tells Next.js this runs in the browser (not server-only),
// because we need window.location to highlight the active link.

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield, UploadCloud, LayoutDashboard,
  FileText, Settings, Activity, ChevronRight
} from "lucide-react";

// Navigation items — add more pages here as you build them
const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard",   icon: LayoutDashboard },
  { href: "/upload",    label: "New Analysis", icon: UploadCloud },
  { href: "/reports",   label: "Reports",      icon: FileText },
  { href: "/activity",  label: "Live Feed",    icon: Activity },
  { href: "/settings",  label: "Settings",     icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname(); // Current URL path, e.g. "/dashboard"

  return (
    <aside className="fixed left-0 top-0 h-full w-64 glass border-r border-teal-700/20 flex flex-col z-50">

      {/* ── Logo ─────────────────────────────────────────────────────── */}
      <div className="p-6 border-b border-teal-700/20">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          {/* Shield icon with animated glow */}
          <div className="relative">
            <div className="w-10 h-10 rounded-lg bg-teal-900/50 border border-teal-600/50
                            flex items-center justify-center group-hover:border-teal-400/70
                            transition-all duration-300">
              <Shield className="w-5 h-5 text-teal-400" />
            </div>
            {/* Pulsing dot — "system is active" */}
            <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-teal-400
                            border-2 border-void-800 animate-pulse" />
          </div>
          <div>
            <div className="font-display text-sm font-bold text-teal-300 tracking-wider">
              ASTRASHIELD
            </div>
            <div className="text-xs font-mono text-slate-500">
              v1.0 · ACTIVE
            </div>
          </div>
        </Link>
      </div>

      {/* ── Navigation Links ──────────────────────────────────────────── */}
      <nav className="flex-1 p-4 space-y-1">
        {/* Section label */}
        <div className="section-label pl-2 mb-4">Navigation</div>

        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-md text-sm font-body
                transition-all duration-200 group relative
                ${isActive
                  ? "bg-teal-900/40 text-teal-300 border border-teal-700/40"
                  : "text-slate-400 hover:text-teal-300 hover:bg-teal-900/20"
                }
              `}
            >
              {/* Left accent bar for active item */}
              {isActive && (
                <div className="absolute left-0 top-2 bottom-2 w-0.5 bg-teal-400 rounded-full" />
              )}

              <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-teal-400" : "text-slate-500 group-hover:text-teal-400"}`} />
              <span>{label}</span>

              {isActive && (
                <ChevronRight className="w-3 h-3 ml-auto text-teal-500" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* ── System Status Footer ──────────────────────────────────────── */}
      <div className="p-4 border-t border-teal-700/20">
        <div className="card p-3">
          <div className="section-label mb-2">System Status</div>
          {/* Each dot shows whether that service is online */}
          {[
            { name: "API Server",  status: "online" },
            { name: "AI Models",   status: "online" },
            { name: "Task Queue",  status: "online" },
          ].map(({ name, status }) => (
            <div key={name} className="flex items-center justify-between py-1">
              <span className="text-xs font-mono text-slate-500">{name}</span>
              <div className="flex items-center gap-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${
                  status === "online" ? "bg-teal-400 animate-pulse" : "bg-red-400"
                }`} />
                <span className={`text-xs font-mono ${
                  status === "online" ? "text-teal-400" : "text-red-400"
                }`}>
                  {status.toUpperCase()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
