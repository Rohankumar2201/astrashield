// app/dashboard/page.tsx — The main dashboard page.
// Shows summary stats, recent analyses, and quick-access buttons.

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Shield, TrendingUp, AlertTriangle, CheckCircle,
  UploadCloud, ChevronRight, Clock, Zap
} from "lucide-react";
import { listReports, getStats, getRiskColor } from "../lib/api";
import type { AnalysisReport, StatsResponse } from "../lib/api";

// Animation helper — fades + slides in from below
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.08, duration: 0.5 }
  }),
};

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [reports, setReports] = useState<AnalysisReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [statsData, reportsData] = await Promise.all([
          getStats(),
          listReports(5),   // Get last 5 reports
        ]);
        setStats(statsData);
        setReports(reportsData.reports || []);
      } catch (e) {
        // Backend not running — show placeholder data for demo
        setStats({ total_analyses: 0, by_risk: {}, threat_rate: 0 });
        setReports([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* ── Page Header ──────────────────────────────────────────────── */}
      <motion.div initial="hidden" animate="visible" variants={fadeUp} custom={0}>
        <div className="section-label">Command Center</div>
        <div className="flex items-end justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold text-white">
              THREAT DASHBOARD
            </h1>
            <p className="text-slate-400 font-body mt-1">
              Real-time AI fraud detection analytics
            </p>
          </div>
          <Link href="/upload" className="btn-primary">
            <UploadCloud className="w-4 h-4" />
            New Analysis
          </Link>
        </div>
      </motion.div>

      {/* ── Stat Cards Row ────────────────────────────────────────────── */}
      <div className="grid grid-cols-4 gap-4">
        {[
          {
            label: "Total Analyses",
            value: stats?.total_analyses ?? "—",
            icon: Shield,
            color: "teal",
            desc: "All time",
          },
          {
            label: "Threat Rate",
            value: stats ? `${stats.threat_rate}%` : "—",
            icon: TrendingUp,
            color: "orange",
            desc: "HIGH + CRITICAL",
          },
          {
            label: "Critical Threats",
            value: stats?.by_risk?.CRITICAL ?? "—",
            icon: AlertTriangle,
            color: "red",
            desc: "Score 86–100",
          },
          {
            label: "Authenticated",
            value: stats?.by_risk?.LOW ?? "—",
            icon: CheckCircle,
            color: "green",
            desc: "Score 0–30",
          },
        ].map(({ label, value, icon: Icon, color, desc }, i) => (
          <motion.div
            key={label}
            className="card"
            initial="hidden" animate="visible" variants={fadeUp} custom={i + 1}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center
                ${color === "teal"   ? "bg-teal-900/50 text-teal-400" :
                  color === "orange" ? "bg-orange-900/50 text-orange-400" :
                  color === "red"    ? "bg-red-900/50 text-red-400" :
                                       "bg-green-900/50 text-green-400"}`}>
                <Icon className="w-5 h-5" />
              </div>
              <Zap className="w-3 h-3 text-slate-600" />
            </div>
            <div className={`font-display text-2xl font-bold mb-1
              ${color === "teal"   ? "text-teal-300" :
                color === "orange" ? "text-orange-400" :
                color === "red"    ? "text-red-400" :
                                     "text-green-400"}`}>
              {loading ? (
                <div className="h-8 w-16 bg-slate-700/50 rounded animate-pulse" />
              ) : value}
            </div>
            <div className="font-body text-sm text-slate-300 font-medium">{label}</div>
            <div className="font-mono text-xs text-slate-600 mt-1">{desc}</div>
          </motion.div>
        ))}
      </div>

      {/* ── Risk Distribution Bar ─────────────────────────────────────── */}
      <motion.div className="card" initial="hidden" animate="visible" variants={fadeUp} custom={5}>
        <div className="section-label mb-4">Risk Distribution</div>
        <div className="flex h-4 rounded-full overflow-hidden gap-0.5">
          {[
            { cat: "CRITICAL", color: "#ef4444" },
            { cat: "HIGH",     color: "#f97316" },
            { cat: "MEDIUM",   color: "#eab308" },
            { cat: "LOW",      color: "#22c55e" },
          ].map(({ cat, color }) => {
            const count = stats?.by_risk?.[cat] || 0;
            const total = stats?.total_analyses || 1;
            const pct = (count / total) * 100;
            return (
              <div
                key={cat}
                className="h-full rounded-sm transition-all duration-1000"
                style={{ width: `${pct}%`, backgroundColor: color, minWidth: pct > 0 ? 4 : 0 }}
                title={`${cat}: ${count}`}
              />
            );
          })}
        </div>
        {/* Legend */}
        <div className="flex gap-6 mt-3">
          {[
            { cat: "CRITICAL", color: "#ef4444", label: "Critical" },
            { cat: "HIGH",     color: "#f97316", label: "High" },
            { cat: "MEDIUM",   color: "#eab308", label: "Medium" },
            { cat: "LOW",      color: "#22c55e", label: "Low" },
          ].map(({ cat, color, label }) => (
            <div key={cat} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-xs font-mono text-slate-500">
                {label}: {stats?.by_risk?.[cat] ?? 0}
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── Recent Analyses Table ─────────────────────────────────────── */}
      <motion.div className="card" initial="hidden" animate="visible" variants={fadeUp} custom={6}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="section-label">Recent Activity</div>
            <h2 className="font-body font-semibold text-white">Latest Analyses</h2>
          </div>
          <Link href="/reports" className="btn-ghost text-sm flex items-center gap-1">
            View All <ChevronRight className="w-3 h-3" />
          </Link>
        </div>

        {loading ? (
          // Skeleton loading state
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-12 bg-slate-800/50 rounded animate-pulse" />
            ))}
          </div>
        ) : reports.length === 0 ? (
          // Empty state
          <div className="text-center py-12">
            <Shield className="w-12 h-12 text-slate-700 mx-auto mb-3" />
            <p className="font-body text-slate-500">No analyses yet</p>
            <p className="font-mono text-xs text-slate-600 mt-1">
              Upload a file to run your first detection
            </p>
            <Link href="/upload" className="btn-primary mt-4 inline-flex">
              <UploadCloud className="w-4 h-4" />
              Upload Now
            </Link>
          </div>
        ) : (
          // Report rows
          <table className="data-table">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Type</th>
                <th>Risk Score</th>
                <th>Category</th>
                <th>Time</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => {
                const color = getRiskColor(r.risk_category);
                return (
                  <tr key={r.job_id} className="hover:bg-teal-900/10 transition-colors">
                    <td>
                      <span className="font-mono text-xs text-teal-400">{r.job_id}</span>
                    </td>
                    <td>
                      <span className="font-mono text-xs text-slate-400 uppercase">
                        {r.file_type}
                      </span>
                    </td>
                    <td>
                      <span className="font-display text-sm font-bold" style={{ color }}>
                        {r.fraud_risk_score}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`badge-${r.risk_category.toLowerCase()}`}
                      >
                        {r.risk_category}
                      </span>
                    </td>
                    <td>
                      <span className="font-mono text-xs text-slate-600 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {r.processing_time_ms}ms
                      </span>
                    </td>
                    <td>
                      <Link
                        href={`/report/${r.job_id}`}
                        className="text-teal-500 hover:text-teal-300 text-xs font-mono flex items-center gap-1"
                      >
                        View <ChevronRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </motion.div>
    </div>
  );
}
