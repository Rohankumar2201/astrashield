// app/components/FraudMeter.tsx — The circular fraud risk gauge.
// This is the most important visual on the report page.
// Shows the 0-100 Fraud Risk Score as an animated arc gauge.

"use client";

import { useEffect, useState } from "react";

interface Props {
  score: number;          // 0-100
  riskCategory: string;   // LOW / MEDIUM / HIGH / CRITICAL
  size?: number;          // SVG size in pixels (default 200)
  animate?: boolean;      // Animate the score counting up
}

// Color for each risk level
const RISK_COLORS: Record<string, string> = {
  LOW:      "#22c55e",
  MEDIUM:   "#eab308",
  HIGH:     "#f97316",
  CRITICAL: "#ef4444",
};

const RISK_LABELS: Record<string, string> = {
  LOW:      "LOW RISK",
  MEDIUM:   "MEDIUM RISK",
  HIGH:     "HIGH RISK",
  CRITICAL: "CRITICAL",
};

export default function FraudMeter({
  score,
  riskCategory,
  size = 200,
  animate = true,
}: Props) {
  const [displayScore, setDisplayScore] = useState(animate ? 0 : score);

  // Animate the score counting up from 0 to the final value
  useEffect(() => {
    if (!animate) return;
    let current = 0;
    const step = Math.ceil(score / 40); // 40 steps total
    const timer = setInterval(() => {
      current = Math.min(current + step, score);
      setDisplayScore(current);
      if (current >= score) clearInterval(timer);
    }, 30); // 30ms per step = ~1.2s total animation
    return () => clearInterval(timer);
  }, [score, animate]);

  const color = RISK_COLORS[riskCategory] || "#6b7280";
  const label = RISK_LABELS[riskCategory] || riskCategory;

  // ── SVG Arc Math ─────────────────────────────────────────────────────────
  // We draw a circular arc from -210° to +30° (240° total sweep)
  // The score (0-100) maps to how much of that arc is filled
  const cx = size / 2;       // Center X
  const cy = size / 2;       // Center Y
  const radius = size * 0.38; // Arc radius
  const strokeWidth = size * 0.06;
  const totalAngle = 240;    // Degrees of arc
  const startAngle = -210;   // Start at bottom-left

  // Convert angle to X,Y coordinates on the circle
  function polarToCartesian(angle: number) {
    const rad = (angle * Math.PI) / 180;
    return {
      x: cx + radius * Math.cos(rad),
      y: cy + radius * Math.sin(rad),
    };
  }

  // Build an SVG arc path
  function describeArc(startDeg: number, endDeg: number) {
    const s = polarToCartesian(startDeg);
    const e = polarToCartesian(endDeg);
    const largeArc = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${radius} ${radius} 0 ${largeArc} 1 ${e.x} ${e.y}`;
  }

  const endAngle = startAngle + (totalAngle * displayScore) / 100;
  const bgPath   = describeArc(startAngle, startAngle + totalAngle);
  const fillPath = describeArc(startAngle, endAngle);

  return (
    <div className="flex flex-col items-center gap-3">
      {/* SVG gauge */}
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="overflow-visible">
          {/* Glow filter definition */}
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background track (gray arc) */}
          <path
            d={bgPath}
            fill="none"
            stroke="rgba(30,41,59,0.8)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Filled arc (colored based on risk) */}
          {displayScore > 0 && (
            <path
              d={fillPath}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              filter="url(#glow)"
              style={{ transition: "stroke 0.3s ease" }}
            />
          )}

          {/* Tick marks at 0, 25, 50, 75, 100 */}
          {[0, 25, 50, 75, 100].map((tick) => {
            const angle = startAngle + (totalAngle * tick) / 100;
            const inner = {
              x: cx + (radius - strokeWidth * 0.8) * Math.cos((angle * Math.PI) / 180),
              y: cy + (radius - strokeWidth * 0.8) * Math.sin((angle * Math.PI) / 180),
            };
            const outer = {
              x: cx + (radius + strokeWidth * 0.8) * Math.cos((angle * Math.PI) / 180),
              y: cy + (radius + strokeWidth * 0.8) * Math.sin((angle * Math.PI) / 180),
            };
            return (
              <line
                key={tick}
                x1={inner.x} y1={inner.y}
                x2={outer.x} y2={outer.y}
                stroke="rgba(71,85,105,0.6)"
                strokeWidth="1.5"
              />
            );
          })}
        </svg>

        {/* Center content: score number + label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div
            className="font-display font-black leading-none"
            style={{
              fontSize: size * 0.22,
              color: color,
              textShadow: `0 0 20px ${color}80`,
            }}
          >
            {displayScore}
          </div>
          <div className="font-mono text-slate-500" style={{ fontSize: size * 0.055 }}>
            / 100
          </div>
          {/* Risk category badge */}
          <div
            className="mt-2 px-3 py-0.5 rounded-full font-mono font-bold border"
            style={{
              fontSize: size * 0.055,
              color: color,
              borderColor: `${color}50`,
              backgroundColor: `${color}15`,
            }}
          >
            {label}
          </div>
        </div>
      </div>

      {/* Score labels below the arc */}
      <div className="flex justify-between w-full px-4 text-xs font-mono text-slate-600">
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>
    </div>
  );
}
