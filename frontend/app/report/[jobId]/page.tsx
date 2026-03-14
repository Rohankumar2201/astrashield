// app/report/[jobId]/page.tsx — The full analysis report page.
// Shows fraud risk meter, per-module breakdown, forensic details.
// [jobId] is a dynamic route segment — the URL is /report/astra_abc123

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft, Shield, Clock, AlertTriangle, CheckCircle,
  FileImage, Music, FileText, ChevronDown, ChevronUp
} from "lucide-react";
import FraudMeter from "../../components/FraudMeter";
import { getReport, getRiskColor } from "../../lib/api";
import type { AnalysisReport } from "../../lib/api";

// Badge component for risk category
function RiskBadge({ category }: { category: string }) {
  const cls = `badge-${category.toLowerCase()}`;
  return <span className={cls}>{category}</span>;
}

// Expandable module card
function ModuleCard({
  title, score, children
}: {
  title: string; score: number; children: React.ReactNode
}) {
  const [open, setOpen] = useState(true);
  const color = score > 60 ? "#ef4444" : score > 30 ? "#f97316" : "#22c55e";

  return (
    <div className="card">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
          <span className="font-body font-semibold text-slate-200">{title}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-display text-sm font-bold" style={{ color }}>
            {score.toFixed(1)}%
          </span>
          {open ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </div>
      </button>

      {/* Score bar */}
      <div className="mt-3 h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, delay: 0.2 }}
        />
      </div>

      {open && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="mt-4 pt-4 border-t border-teal-900/30"
        >
          {children}
        </motion.div>
      )}
    </div>
  );
}

export default function ReportPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const router = useRouter();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const data = await getReport(jobId);
        setReport(data);
      } catch (e: any) {
        setError(e.response?.data?.detail || "Could not load report");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [jobId]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
          <p className="font-mono text-teal-500">Loading report...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-5xl mx-auto card text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
        <p className="font-body text-red-300">{error || "Report not found"}</p>
        <button onClick={() => router.push("/reports")} className="btn-ghost mt-4 mx-auto">
          Back to Reports
        </button>
      </div>
    );
  }

  const riskColor = getRiskColor(report.risk_category);
  const modules = report.modules || {};

  return (
    <div className="max-w-5xl mx-auto space-y-8">

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-sm font-mono text-slate-500
                       hover:text-teal-400 transition-colors mb-3"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </button>
          <div className="section-label">Analysis Report</div>
          <h1 className="font-display text-2xl font-bold text-white">
            {report.job_id.toUpperCase()}
          </h1>
          <div className="flex items-center gap-4 mt-2">
            <span className="font-mono text-xs text-slate-500">
              {new Date(report.timestamp).toLocaleString()}
            </span>
            <span className="font-mono text-xs text-slate-500 uppercase">
              {report.file_type}
            </span>
            <span className="flex items-center gap-1 font-mono text-xs text-slate-500">
              <Clock className="w-3 h-3" />
              {report.processing_time_ms}ms
            </span>
          </div>
        </div>
        <RiskBadge category={report.risk_category} />
      </div>

      {/* ── Main Content: Meter + Recommendation ─────────────────────── */}
      <div className="grid grid-cols-2 gap-6">

        {/* Fraud Risk Meter */}
        <div className="card flex flex-col items-center py-8">
          <div className="section-label mb-6">Fraud Risk Score</div>
          <FraudMeter
            score={report.fraud_risk_score}
            riskCategory={report.risk_category}
            size={220}
          />
        </div>

        {/* Recommendation box */}
        <div className="card flex flex-col justify-between">
          <div>
            <div className="section-label mb-3">Recommendation</div>
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 border"
              style={{ backgroundColor: `${riskColor}15`, borderColor: `${riskColor}40` }}
            >
              {report.risk_category === "LOW" ? (
                <CheckCircle className="w-6 h-6" style={{ color: riskColor }} />
              ) : (
                <AlertTriangle className="w-6 h-6" style={{ color: riskColor }} />
              )}
            </div>
            <p className="font-body text-slate-300 text-sm leading-relaxed">
              {report.recommendation}
            </p>
          </div>

          {/* Module score summary */}
          <div className="mt-6 pt-6 border-t border-teal-900/30 space-y-2">
            <div className="section-label mb-3">Module Summary</div>
            {Object.entries(modules).map(([name, data]: [string, any]) => {
              const score = data?.score ?? 0;
              const c = score > 60 ? "#ef4444" : score > 30 ? "#f97316" : "#22c55e";
              return (
                <div key={name} className="flex items-center justify-between">
                  <span className="font-mono text-xs text-slate-500 capitalize">
                    {name.replace(/_/g, " ")}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-1 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${score}%`, backgroundColor: c }} />
                    </div>
                    <span className="font-mono text-xs font-bold w-10 text-right" style={{ color: c }}>
                      {score.toFixed(0)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Per-Module Detail Cards ───────────────────────────────────── */}
      <div>
        <div className="section-label mb-4">Detailed Module Analysis</div>
        <div className="space-y-4">

          {/* IMAGE MODULE */}
          {modules.image_deepfake && (
            <ModuleCard title="Image Deepfake Detection" score={modules.image_deepfake.score}>
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-3 text-center">
                  {[
                    { label: "Model",    value: modules.image_deepfake.model },
                    { label: "Faces",    value: modules.image_deepfake.faces_detected ?? 0 },
                    { label: "Score",    value: `${modules.image_deepfake.score}%` },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-void-700/50 rounded-lg p-3">
                      <div className="font-mono text-xs text-slate-500 mb-1">{label}</div>
                      <div className="font-body text-sm font-semibold text-slate-200">{String(value)}</div>
                    </div>
                  ))}
                </div>

                {/* Face bounding boxes */}
                {modules.image_deepfake.face_results?.length > 0 && (
                  <div>
                    <div className="section-label mb-2">Face Analysis Results</div>
                    {modules.image_deepfake.face_results.map((face: any, i: number) => (
                      <div key={i} className="flex items-center justify-between py-2 border-b border-teal-900/20">
                        <span className="font-mono text-xs text-slate-500">Face #{i + 1}</span>
                        <span className="font-mono text-xs text-slate-400">
                          Deepfake probability: {(face.deepfake_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </ModuleCard>
          )}

          {/* ELA MODULE */}
          {modules.ela_analysis && (
            <ModuleCard title="Error Level Analysis (ELA)" score={modules.ela_analysis.score}>
              <div className="space-y-3">
                <p className="font-body text-xs text-slate-500 leading-relaxed">
                  ELA detects image tampering by analyzing JPEG compression inconsistencies.
                  Edited regions appear brighter in the ELA map.
                </p>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: "Score",          value: `${modules.ela_analysis.score}%` },
                    { label: "Mean Diff",      value: modules.ela_analysis.mean_diff ?? "—" },
                    { label: "Interpretation", value: modules.ela_analysis.interpretation ?? "—" },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-void-700/50 rounded-lg p-3 text-center">
                      <div className="font-mono text-xs text-slate-500 mb-1">{label}</div>
                      <div className="font-body text-sm font-semibold text-slate-200">{String(value)}</div>
                    </div>
                  ))}
                </div>
                {/* ELA image from backend */}
                {modules.ela_analysis.ela_image && (
                  <div>
                    <div className="section-label mb-2">ELA Map</div>
                    <img
                      src={`data:image/png;base64,${modules.ela_analysis.ela_image}`}
                      alt="ELA Map"
                      className="w-full max-h-48 object-contain rounded-lg border border-teal-900/30"
                    />
                    <p className="font-mono text-xs text-slate-600 mt-1">
                      Brighter areas indicate potential manipulation
                    </p>
                  </div>
                )}
              </div>
            </ModuleCard>
          )}

          {/* AUDIO MODULE */}
          {modules.voice_clone_detection && (
            <ModuleCard title="Voice Clone Detection" score={modules.voice_clone_detection.score}>
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: "Model",     value: "ResNet-18 CNN" },
                    { label: "Duration",  value: `${modules.voice_clone_detection.duration_seconds}s` },
                    { label: "Sample Rate", value: `${modules.voice_clone_detection.sample_rate} Hz` },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-void-700/50 rounded-lg p-3 text-center">
                      <div className="font-mono text-xs text-slate-500 mb-1">{label}</div>
                      <div className="font-body text-sm font-semibold text-slate-200">{value}</div>
                    </div>
                  ))}
                </div>
                <div className="flex gap-4">
                  <div className="flex-1 bg-green-900/20 border border-green-700/30 rounded-lg p-3 text-center">
                    <div className="font-mono text-xs text-green-600 mb-1">Real Voice</div>
                    <div className="font-display text-xl font-bold text-green-400">
                      {modules.voice_clone_detection.real_probability}%
                    </div>
                  </div>
                  <div className="flex-1 bg-red-900/20 border border-red-700/30 rounded-lg p-3 text-center">
                    <div className="font-mono text-xs text-red-600 mb-1">AI Clone</div>
                    <div className="font-display text-xl font-bold text-red-400">
                      {modules.voice_clone_detection.fake_probability}%
                    </div>
                  </div>
                </div>
                {/* Spectrogram image */}
                {modules.voice_clone_detection.spectrogram_image && (
                  <div>
                    <div className="section-label mb-2">Mel Spectrogram</div>
                    <img
                      src={`data:image/png;base64,${modules.voice_clone_detection.spectrogram_image}`}
                      alt="Mel Spectrogram"
                      className="w-full max-h-40 object-fill rounded-lg border border-teal-900/30"
                    />
                    <p className="font-mono text-xs text-slate-600 mt-1">
                      Frequency patterns over time — AI clones show unnatural harmonics
                    </p>
                  </div>
                )}
              </div>
            </ModuleCard>
          )}

          {/* METADATA MODULE */}
          {modules.metadata_forensics && (
            <ModuleCard title="Metadata Forensic Analysis" score={modules.metadata_forensics.score}>
              <div className="space-y-3">
                {modules.metadata_forensics.flags?.length > 0 ? (
                  <div className="space-y-2">
                    <div className="section-label">Flags Detected</div>
                    {modules.metadata_forensics.flags.map((flag: string, i: number) => (
                      <div key={i} className="flex items-start gap-2 p-2 bg-red-900/10 border border-red-700/20 rounded">
                        <AlertTriangle className="w-3 h-3 text-red-400 flex-shrink-0 mt-0.5" />
                        <span className="font-mono text-xs text-red-400">{flag}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center gap-2 p-2 bg-green-900/10 border border-green-700/20 rounded">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-mono text-xs text-green-400">No metadata anomalies detected</span>
                  </div>
                )}
              </div>
            </ModuleCard>
          )}
        </div>
      </div>

      {/* Raw JSON (for developers) */}
      <details className="card">
        <summary className="cursor-pointer font-mono text-xs text-slate-500 hover:text-slate-300">
          View Raw JSON Report
        </summary>
        <pre className="mt-4 text-xs font-mono text-green-400 overflow-auto max-h-64 p-4
                        bg-black/50 rounded-lg border border-teal-900/20">
          {JSON.stringify(report, null, 2)}
        </pre>
      </details>
    </div>
  );
}
