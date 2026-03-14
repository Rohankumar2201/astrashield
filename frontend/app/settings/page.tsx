// app/settings/page.tsx — Settings page.

"use client";

import { useState } from "react";
import { Settings, Save, CheckCircle } from "lucide-react";

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  );
  const [saved, setSaved] = useState(false);

  function handleSave() {
    // In a real app, save to localStorage or a config file
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">

      <div>
        <div className="section-label">Configuration</div>
        <h1 className="font-display text-3xl font-bold text-white">SETTINGS</h1>
      </div>

      {/* API Config */}
      <div className="card space-y-6">
        <div>
          <div className="section-label mb-1">API Configuration</div>
          <h2 className="font-body font-semibold text-white">Backend Connection</h2>
        </div>

        <div>
          <label className="font-mono text-xs text-slate-500 block mb-2">
            API Base URL
          </label>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="w-full bg-void-700/50 border border-teal-700/30 rounded-lg px-4 py-2.5
                       font-mono text-sm text-slate-300
                       focus:outline-none focus:border-teal-500/60"
          />
          <p className="font-mono text-xs text-slate-600 mt-1">
            Set to your FastAPI backend URL (default: http://localhost:8000)
          </p>
        </div>

        <button onClick={handleSave} className="btn-primary">
          {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saved ? "Saved!" : "Save Settings"}
        </button>
      </div>

      {/* Detection thresholds */}
      <div className="card space-y-6">
        <div>
          <div className="section-label mb-1">Detection Thresholds</div>
          <h2 className="font-body font-semibold text-white">Risk Score Calibration</h2>
        </div>

        {[
          { label: "LOW → MEDIUM",   value: 30, color: "#eab308" },
          { label: "MEDIUM → HIGH",  value: 60, color: "#f97316" },
          { label: "HIGH → CRITICAL",value: 85, color: "#ef4444" },
        ].map(({ label, value, color }) => (
          <div key={label} className="flex items-center justify-between">
            <span className="font-mono text-sm text-slate-400">{label}</span>
            <div className="flex items-center gap-3">
              <div className="w-32 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${value}%`, backgroundColor: color }} />
              </div>
              <span className="font-display text-sm font-bold w-8" style={{ color }}>{value}</span>
            </div>
          </div>
        ))}

        <p className="font-mono text-xs text-slate-600">
          Thresholds are set in backend/scoring/ensemble.py → RISK_THRESHOLDS
        </p>
      </div>

      {/* About */}
      <div className="card">
        <div className="section-label mb-3">About</div>
        <div className="space-y-2">
          {[
            ["Project",  "AstraShield"],
            ["Version",  "1.0.0"],
            ["Track",    "Cybersecurity + Generative AI"],
            ["Event",    "IIT Bombay Hack & Break 2024"],
            ["Stack",    "Next.js 14 · FastAPI · PyTorch · Redis"],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between py-2 border-b border-teal-900/20 last:border-0">
              <span className="font-mono text-xs text-slate-500">{k}</span>
              <span className="font-mono text-xs text-teal-400">{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
