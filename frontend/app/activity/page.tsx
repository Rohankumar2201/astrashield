// app/activity/page.tsx — Live feed page showing incoming analyses.
// Auto-refreshes every 5 seconds.

"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Zap, AlertTriangle, CheckCircle } from "lucide-react";
import { listReports, getRiskColor } from "../lib/api";
import type { AnalysisReport } from "../lib/api";

export default function ActivityPage() {
  const [reports, setReports] = useState<AnalysisReport[]>([]);
  const [newIds, setNewIds] = useState<Set<string>>(new Set());
  const prevIdsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    async function refresh() {
      try {
        const data = await listReports(20);
        const incoming: AnalysisReport[] = data.reports || [];
        const freshIds = new Set<string>(incoming.map((r: AnalysisReport) => r.job_id));

        // Find which ones are brand new
        const brandNew = incoming
          .filter((r: AnalysisReport) => !prevIdsRef.current.has(r.job_id))
          .map((r: AnalysisReport) => r.job_id);

        if (brandNew.length > 0) {
          setNewIds(new Set(brandNew));
          setTimeout(() => setNewIds(new Set()), 3000); // Remove highlight after 3s
        }

        prevIdsRef.current = freshIds;
        setReports(incoming);
      } catch {/* backend offline */}
    }

    refresh();
    const interval = setInterval(refresh, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8">

      <div className="flex items-center justify-between">
        <div>
          <div className="section-label">Real-Time</div>
          <h1 className="font-display text-3xl font-bold text-white">LIVE FEED</h1>
        </div>
        {/* Pulsing "live" indicator */}
        <div className="flex items-center gap-2 px-4 py-2 bg-teal-900/20 border border-teal-700/30 rounded-full">
          <div className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
          <span className="font-mono text-xs text-teal-400">LIVE · Refreshes every 5s</span>
        </div>
      </div>

      {/* Feed */}
      <div className="space-y-3">
        <AnimatePresence>
          {reports.length === 0 ? (
            <div className="card text-center py-16">
              <Activity className="w-12 h-12 text-slate-700 mx-auto mb-3" />
              <p className="font-body text-slate-500">Waiting for analyses...</p>
              <p className="font-mono text-xs text-slate-600 mt-1">
                Upload a file to see live feed activity
              </p>
            </div>
          ) : reports.map((r) => {
            const color = getRiskColor(r.risk_category);
            const isNew  = newIds.has(r.job_id);
            return (
              <motion.div
                key={r.job_id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`
                  card flex items-center gap-4 cursor-pointer transition-all
                  ${isNew ? "border-teal-500/60 shadow-teal-glow" : ""}
                `}
                onClick={() => window.location.href = `/report/${r.job_id}`}
              >
                {/* Risk color dot */}
                <div className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}60` }}
                />

                {/* Job info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm text-teal-400">{r.job_id}</span>
                    {isNew && (
                      <span className="px-1.5 py-0.5 bg-teal-500/20 text-teal-400
                                       rounded text-xs font-mono border border-teal-500/30">
                        NEW
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="font-mono text-xs text-slate-600 uppercase">{r.file_type}</span>
                    <span className="font-mono text-xs text-slate-600">
                      {new Date(r.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                {/* Score */}
                <div className="text-right">
                  <div className="font-display text-xl font-bold" style={{ color }}>
                    {r.fraud_risk_score}
                  </div>
                  <div className="font-mono text-xs" style={{ color }}>
                    {r.risk_category}
                  </div>
                </div>

                {/* Icon */}
                <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${color}15`, border: `1px solid ${color}30` }}>
                  {r.risk_category === "LOW" ? (
                    <CheckCircle className="w-4 h-4" style={{ color }} />
                  ) : (
                    <AlertTriangle className="w-4 h-4" style={{ color }} />
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
