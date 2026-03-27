// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      colors: {
        et: {
          red: "#E8002D",
          dark: "#0A0A0A",
          card: "#111111",
          border: "#1E1E1E",
          muted: "#2A2A2A",
        },
      },
      animation: {
        "slide-in": "slideIn 0.3s ease forwards",
        "pulse-dot": "pulseDot 1.5s ease-in-out infinite",
        "fade-in": "fadeIn 0.4s ease forwards",
      },
      keyframes: {
        slideIn: {
          "0%": { opacity: 0, transform: "translateY(8px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        pulseDot: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.3 },
        },
        fadeIn: {
          "0%": { opacity: 0 },
          "100%": { opacity: 1 },
        },
      },
    },
  },
  plugins: [],
};
