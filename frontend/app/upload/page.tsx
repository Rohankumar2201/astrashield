// app/upload/page.tsx — The file upload page.
// Users drag-and-drop or click to pick a file, then watch live analysis progress.

"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  UploadCloud, FileImage, Music, FileText,
  CheckCircle, AlertCircle, Loader2, Shield, X
} from "lucide-react";
import { uploadFile, pollUntilComplete } from "../lib/api";
import type { JobStatus } from "../lib/api";

// Accepted file types mapped to display info
const FILE_TYPES = [
  { label: "Images",    exts: ".jpg .png .webp", icon: FileImage, desc: "Deepfake face detection" },
  { label: "Audio",     exts: ".mp3 .wav .m4a",  icon: Music,     desc: "Voice clone detection" },
  { label: "Documents", exts: ".pdf",            icon: FileText,  desc: "Document forgery detection" },
];

// Each step in the pipeline with its display label
const PIPELINE_STEPS = [
  { key: "upload",        label: "File Upload" },
  { key: "preprocessing", label: "Preprocessing" },
  { key: "ai_analysis",   label: "AI Analysis" },
  { key: "scoring",       label: "Fraud Scoring" },
  { key: "report",        label: "Report Generation" },
];

type UploadState = "idle" | "uploading" | "analyzing" | "done" | "error";

export default function UploadPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [notes, setNotes] = useState("");
  const [state, setState] = useState<UploadState>("idle");
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [jobId, setJobId] = useState("");

  // ── Drag-and-drop handler ──────────────────────────────────────────────
  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) {
      setSelectedFile(accepted[0]);
      setState("idle");
      setErrorMsg("");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/webp": [".webp"],
      "audio/mpeg": [".mp3"],
      "audio/wav": [".wav"],
      "audio/mp4": [".m4a"],
      "application/pdf": [".pdf"],
    },
  });

  // ── Submit handler ─────────────────────────────────────────────────────
  async function handleAnalyze() {
    if (!selectedFile) return;

    try {
      // Step 1: Upload the file
      setState("uploading");
      const uploadResult = await uploadFile(selectedFile, notes);
      setJobId(uploadResult.job_id);

      // Step 2: Poll until analysis is complete
      setState("analyzing");
      const finalStatus = await pollUntilComplete(
        uploadResult.job_id,
        (status) => setJobStatus(status), // Called on every poll
        2000,  // Poll every 2 seconds
        90     // Max 90 attempts = 3 minutes
      );

      if (finalStatus.status === "completed") {
        setState("done");
        // Redirect to the report page after a short delay
        setTimeout(() => router.push(`/report/${uploadResult.job_id}`), 1200);
      } else {
        throw new Error(finalStatus.error || "Analysis failed");
      }

    } catch (err: any) {
      setState("error");
      setErrorMsg(err.response?.data?.detail || err.message || "Unknown error");
    }
  }

  // ── Progress calculation ───────────────────────────────────────────────
  const progress = jobStatus?.progress ?? 0;

  return (
    <div className="max-w-3xl mx-auto space-y-8">

      {/* Header */}
      <div>
        <div className="section-label">Detection Engine</div>
        <h1 className="font-display text-3xl font-bold text-white">NEW ANALYSIS</h1>
        <p className="text-slate-400 font-body mt-1">
          Upload media for AI-powered fraud detection
        </p>
      </div>

      {/* Accepted file types info */}
      <div className="grid grid-cols-3 gap-3">
        {FILE_TYPES.map(({ label, exts, icon: Icon, desc }) => (
          <div key={label} className="card p-4 flex items-start gap-3">
            <div className="w-8 h-8 rounded-md bg-teal-900/50 flex items-center justify-center flex-shrink-0">
              <Icon className="w-4 h-4 text-teal-400" />
            </div>
            <div>
              <div className="font-body text-sm font-semibold text-slate-200">{label}</div>
              <div className="font-mono text-xs text-slate-500">{exts}</div>
              <div className="font-mono text-xs text-teal-600 mt-0.5">{desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-300
          ${isDragActive
            ? "border-teal-400 bg-teal-900/20 shadow-teal-glow"
            : selectedFile
            ? "border-teal-600/60 bg-teal-900/10"
            : "border-slate-700 hover:border-teal-700 hover:bg-teal-900/10"
          }
          ${state !== "idle" ? "pointer-events-none" : ""}
        `}
      >
        <input {...getInputProps()} />

        {/* Corner accent lines */}
        <div className="absolute top-3 left-3 w-6 h-6 border-t-2 border-l-2 border-teal-500/50 rounded-tl-md" />
        <div className="absolute top-3 right-3 w-6 h-6 border-t-2 border-r-2 border-teal-500/50 rounded-tr-md" />
        <div className="absolute bottom-3 left-3 w-6 h-6 border-b-2 border-l-2 border-teal-500/50 rounded-bl-md" />
        <div className="absolute bottom-3 right-3 w-6 h-6 border-b-2 border-r-2 border-teal-500/50 rounded-br-md" />

        <AnimatePresence mode="wait">
          {selectedFile ? (
            <motion.div
              key="selected"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <div className="w-16 h-16 rounded-xl bg-teal-900/50 border border-teal-600/50
                              flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-teal-400" />
              </div>
              <p className="font-body font-semibold text-teal-300 text-lg">
                {selectedFile.name}
              </p>
              <p className="font-mono text-sm text-slate-500 mt-1">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                · {selectedFile.type || "unknown type"}
              </p>
              {state === "idle" && (
                <button
                  onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                  className="mt-3 text-xs font-mono text-slate-600 hover:text-slate-400
                             flex items-center gap-1 mx-auto transition-colors"
                >
                  <X className="w-3 h-3" /> Remove file
                </button>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="w-16 h-16 rounded-xl bg-slate-800/50 border border-slate-700
                              flex items-center justify-center mx-auto mb-4">
                <UploadCloud className={`w-8 h-8 ${isDragActive ? "text-teal-400" : "text-slate-500"}`} />
              </div>
              <p className="font-body font-semibold text-slate-300 text-lg">
                {isDragActive ? "Drop it here" : "Drag & drop or click to browse"}
              </p>
              <p className="font-mono text-sm text-slate-600 mt-2">
                Images · Audio · PDFs · Max 50MB
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Notes field */}
      {selectedFile && state === "idle" && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <label className="section-label block mb-2">Analyst Notes (optional)</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add context about this submission..."
            rows={3}
            className="w-full bg-void-800 border border-teal-700/30 rounded-lg p-3
                       font-body text-sm text-slate-300 placeholder-slate-600
                       focus:outline-none focus:border-teal-500/60 resize-none"
          />
        </motion.div>
      )}

      {/* Analyze button */}
      {selectedFile && state === "idle" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <button onClick={handleAnalyze} className="btn-primary w-full justify-center py-4 text-base">
            <Shield className="w-5 h-5" />
            Run Fraud Analysis
          </button>
        </motion.div>
      )}

      {/* ── Analysis Progress ─────────────────────────────────────────── */}
      <AnimatePresence>
        {(state === "uploading" || state === "analyzing" || state === "done") && (
          <motion.div
            className="card space-y-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            {/* Overall progress bar */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="section-label">
                  {state === "uploading" ? "Uploading..." :
                   state === "done"      ? "Analysis Complete!" :
                   "Analyzing..."}
                </span>
                <span className="font-mono text-sm text-teal-400">{progress}%</span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-teal-600 to-teal-400 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>

            {/* Pipeline steps */}
            <div className="space-y-3">
              {PIPELINE_STEPS.map(({ key, label }) => {
                const stepStatus = jobStatus?.steps?.[key as keyof typeof jobStatus.steps] ?? "pending";
                const isCompleted = stepStatus === "completed";
                const isActive    = !isCompleted && jobStatus?.status === "processing" &&
                  PIPELINE_STEPS.findIndex(s => s.key === key) ===
                  PIPELINE_STEPS.findIndex(s => jobStatus?.steps?.[s.key as keyof typeof jobStatus.steps] !== "completed");

                return (
                  <div key={key} className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                      ${isCompleted ? "bg-teal-900/50 text-teal-400" :
                        isActive    ? "bg-teal-900/30 text-teal-500" :
                                      "bg-slate-800 text-slate-600"}`}>
                      {isCompleted ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : isActive ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        <div className="w-1.5 h-1.5 rounded-full bg-current" />
                      )}
                    </div>
                    <span className={`font-body text-sm ${
                      isCompleted ? "text-teal-300" :
                      isActive    ? "text-slate-300" :
                                    "text-slate-600"
                    }`}>
                      {label}
                    </span>
                    {isCompleted && (
                      <span className="ml-auto font-mono text-xs text-teal-600">✓ Done</span>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Done: auto-redirect notice */}
            {state === "done" && (
              <motion.div
                className="text-center p-4 bg-teal-900/20 border border-teal-700/30 rounded-lg"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <CheckCircle className="w-8 h-8 text-teal-400 mx-auto mb-2" />
                <p className="font-body text-teal-300 font-semibold">Analysis Complete</p>
                <p className="font-mono text-xs text-slate-500 mt-1">
                  Redirecting to report...
                </p>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error state */}
      {state === "error" && (
        <motion.div
          className="card border-red-700/40 bg-red-900/10 p-6 flex items-start gap-4"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        >
          <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-body font-semibold text-red-300">Analysis Failed</p>
            <p className="font-mono text-sm text-red-500/80 mt-1">{errorMsg}</p>
            <button
              onClick={() => { setState("idle"); setJobStatus(null); }}
              className="mt-3 text-sm font-mono text-slate-400 hover:text-slate-200 underline"
            >
              Try again
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
