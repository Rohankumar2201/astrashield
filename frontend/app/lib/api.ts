// app/lib/api.ts — Central API client.
// All network requests go through here, so if the backend URL changes,
// you only have to update it in one place.

import axios from "axios";

// Base URL of the backend. Set in .env.local
const API_BASE = "";

// Create an axios instance with default settings
export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60 seconds (model inference can be slow)
});

// ── TypeScript type definitions ────────────────────────────────────────────
// These describe the shape of data we receive from the backend.

export interface UploadResponse {
  job_id: string;
  filename: string;
  file_type: string;
  status: string;
  message: string;
}

export interface JobStatus {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;    // 0-100
  created_at: string;
  error?: string;
  steps: {
    upload: string;
    preprocessing: string;
    ai_analysis: string;
    scoring: string;
    report: string;
  };
}

export interface AnalysisReport {
  job_id: string;
  timestamp: string;
  file_type: "image" | "audio" | "document";
  fraud_risk_score: number;       // 0-100
  risk_category: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  recommendation: string;
  processing_time_ms: number;
  modules: Record<string, any>;   // Varies by file type
}

export interface StatsResponse {
  total_analyses: number;
  by_risk: Record<string, number>;
  threat_rate: number;
}

// ── API Functions ──────────────────────────────────────────────────────────

/**
 * Upload a file for analysis.
 * Returns a job_id you can use to track progress.
 */
export async function uploadFile(file: File, notes = ""): Promise<UploadResponse> {
  // FormData is how browsers send file uploads
  const formData = new FormData();
  formData.append("file", file);
  formData.append("notes", notes);

  const response = await api.post<UploadResponse>("/api/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

/**
 * Poll job status. Call this every 2 seconds until status = "completed".
 */
export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await api.get<JobStatus>(`/api/analyze/status/${jobId}`);
  return response.data;
}

/**
 * Get the full analysis result once a job is completed.
 */
export async function getAnalysisResult(jobId: string): Promise<AnalysisReport> {
  const response = await api.get<AnalysisReport>(`/api/analyze/result/${jobId}`);
  return response.data;
}

/**
 * Get all past reports for the reports list page.
 */
export async function listReports(limit = 20, skip = 0) {
  const response = await api.get("/api/report/list", { params: { limit, skip } });
  return response.data;
}

/**
 * Get a single report by job_id.
 */
export async function getReport(jobId: string): Promise<AnalysisReport> {
  const response = await api.get<AnalysisReport>(`/api/report/${jobId}`);
  return response.data;
}

/**
 * Get summary stats for the dashboard header.
 */
export async function getStats(): Promise<StatsResponse> {
  const response = await api.get<StatsResponse>("/api/report/stats/summary");
  return response.data;
}

/**
 * Delete a report.
 */
export async function deleteReport(jobId: string) {
  await api.delete(`/api/report/${jobId}`);
}

// ── Helper Functions ───────────────────────────────────────────────────────

/**
 * Poll a job until it completes or fails.
 * Calls onProgress with status updates while waiting.
 * 
 * Usage:
 *   const result = await pollUntilComplete("job_id_123", (status) => {
 *     setProgress(status.progress);
 *   });
 */
export async function pollUntilComplete(
  jobId: string,
  onProgress?: (status: JobStatus) => void,
  intervalMs = 2000,
  maxAttempts = 60
): Promise<JobStatus> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const status = await getJobStatus(jobId);
    onProgress?.(status);

    if (status.status === "completed" || status.status === "failed") {
      return status;
    }

    // Wait before polling again
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
  throw new Error("Analysis timed out after 2 minutes");
}

/**
 * Returns the CSS color for a risk category string.
 */
export function getRiskColor(category: string): string {
  const colors: Record<string, string> = {
    LOW:      "#22c55e",
    MEDIUM:   "#eab308",
    HIGH:     "#f97316",
    CRITICAL: "#ef4444",
  };
  return colors[category] || "#6b7280";
}
