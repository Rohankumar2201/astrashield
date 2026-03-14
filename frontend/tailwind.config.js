/** @type {import('tailwindcss').Config} */
module.exports = {
  // Tell Tailwind where to look for class names
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Custom colors for the cyberpunk theme
      colors: {
        // Primary teal palette
        teal: {
          400: "#2dd4bf",
          500: "#14b8a6",
          600: "#0d9488",
          700: "#0f766e",
          900: "#042f2e",
        },
        // Dark background palette
        void: {
          900: "#020818",   // Deepest background
          800: "#040d1f",   // Card backgrounds
          700: "#071428",   // Slightly lighter
          600: "#0a1a30",   // Borders/dividers
        },
      },
      // Custom fonts
      fontFamily: {
        mono:    ["'Space Mono'", "monospace"],
        display: ["'Orbitron'", "sans-serif"],
        body:    ["'IBM Plex Sans'", "sans-serif"],
      },
      // Custom animations
      animation: {
        "pulse-teal":   "pulse-teal 2s ease-in-out infinite",
        "scan":         "scan 3s linear infinite",
        "glow":         "glow 2s ease-in-out infinite alternate",
        "flicker":      "flicker 0.15s infinite",
        "spin-slow":    "spin 4s linear infinite",
      },
      keyframes: {
        "pulse-teal": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(13,148,136,0.4)" },
          "50%":       { boxShadow: "0 0 0 12px rgba(13,148,136,0)" },
        },
        scan: {
          "0%":   { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        glow: {
          from: { textShadow: "0 0 8px #0d9488, 0 0 16px #0d9488" },
          to:   { textShadow: "0 0 16px #2dd4bf, 0 0 32px #2dd4bf, 0 0 48px #0d9488" },
        },
        flicker: {
          "0%, 100%": { opacity: 1 },
          "50%":       { opacity: 0.85 },
        },
      },
      // Box shadow utilities
      boxShadow: {
        "teal-glow":     "0 0 20px rgba(13,148,136,0.4), 0 0 40px rgba(13,148,136,0.2)",
        "teal-glow-lg":  "0 0 40px rgba(13,148,136,0.5), 0 0 80px rgba(13,148,136,0.25)",
        "red-glow":      "0 0 20px rgba(239,68,68,0.4),  0 0 40px rgba(239,68,68,0.2)",
        "card":          "0 4px 24px rgba(0,0,0,0.4)",
      },
    },
  },
  plugins: [],
};
