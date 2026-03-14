// app/reports/page.tsx — List all past analysis reports.

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { FileText, ChevronRight, Clock, Filter, Search } from "lucide-react";
import { listReports, getRiskColor } from "../lib/api";
import type { AnalysisReport } from "../lib/api";

export default function ReportsPage() {
  const [reports, setReports] = useState<AnalysisReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await listReports(50);
        setReports(data.reports || []);
      } catch {
        setReports([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Filter by risk category and search term
  const filtered = reports.filter((r) => {
    const matchesFilter = filter === "ALL" || r.risk_category === filter;
    const matchesSearch = r.job_id.toLowerCase().includes(search.toLowerCase()) ||
                          r.file_type.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="max-w-5xl mx-auto space-y-8">

      {/* Header */}
      <div>
        <div className="section-label">Analysis History</div>
        <h1 className="font-display text-3xl font-bold text-white">REPORTS</h1>
        <p className="text-slate-400 font-body mt-1">All past fraud detection analyses</p>
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by job ID or type..."
            className="w-full bg-void-800 border border-teal-700/30 rounded-lg pl-10 pr-4 py-2.5
                       font-mono text-sm text-slate-300 placeholder-slate-600
                       focus:outline-none focus:border-teal-500/60"
          />
        </div>

        {/* Category filter buttons */}
        <div className="flex gap-2">
          {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-3 py-1.5 rounded-md text-xs font-mono transition-all ${
                filter === cat
                  ? "bg-teal-700/40 text-teal-300 border border-teal-600/50"
                  : "text-slate-500 hover:text-teal-400 border border-transparent"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Reports table */}
      <div className="card">
        {loading ? (
          <div className="space-y-3">
            {[1,2,3,4,5].map(i => (
              <div key={i} className="h-14 bg-slate-800/50 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <FileText className="w-12 h-12 text-slate-700 mx-auto mb-3" />
            <p className="font-body text-slate-500">
              {reports.length === 0 ? "No reports yet" : "No reports match your filter"}
            </p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Type</th>
                <th>Risk Score</th>
                <th>Category</th>
                <th>Analyzed At</th>
                <th>Time</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => {
                const color = getRiskColor(r.risk_category);
                return (
                  <motion.tr
                    key={r.job_id}
                    className="hover:bg-teal-900/10 transition-colors cursor-pointer"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    onClick={() => window.location.href = `/report/${r.job_id}`}
                  >
                    <td>
                      <span className="font-mono text-xs text-teal-400">{r.job_id}</span>
                    </td>
                    <td>
                      <span className="font-mono text-xs text-slate-400 uppercase bg-slate-800/50 px-2 py-0.5 rounded">
                        {r.file_type}
                      </span>
                    </td>
                    <td>
                      {/* Mini gauge bar */}
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${r.fraud_risk_score}%`, backgroundColor: color }}
                          />
                        </div>
                        <span className="font-display text-sm font-bold" style={{ color }}>
                          {r.fraud_risk_score}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className={`badge-${r.risk_category.toLowerCase()}`}>
                        {r.risk_category}
                      </span>
                    </td>
                    <td>
                      <span className="font-mono text-xs text-slate-500">
                        {new Date(r.timestamp).toLocaleDateString()}
                      </span>
                    </td>
                    <td>
                      <span className="font-mono text-xs text-slate-600 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {r.processing_time_ms}ms
                      </span>
                    </td>
                    <td>
                      <ChevronRight className="w-4 h-4 text-slate-600" />
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
