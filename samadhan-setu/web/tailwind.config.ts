import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "var(--primary)", hover: "var(--primary-hover)", soft: "var(--primary-soft)" },
        secondary: "var(--secondary)",
        accent: "var(--accent)",
        accent2: "var(--accent-2)",
        surface: { light: "var(--surface-light)", dark: "var(--surface-dark)" },
        border: { light: "var(--border-light)", dark: "var(--border-dark)" },
        text: { light: "var(--text-light)", dark: "var(--text-dark)" },
        muted: "var(--muted)",
        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",
        info: "var(--info)",
        domain: {
          agriculture: "#16A34A",
          healthcare: "#DC2626",
          water_resources: "#0EA5E9",
          education: "#4F46E5",
          energy: "#F59E0B",
          environment: "#14B8A6",
          urban_development: "#8B5CF6",
          accessibility: "#EC4899",
          public_administration: "#64748B",
          rural_livelihoods: "#D97706",
        },
      },
      fontFamily: {
        sora: ["var(--font-sora)"],
        inter: ["var(--font-inter)"],
        mono: ["var(--font-jetbrains)"],
        devanagari: ["var(--font-noto-devanagari)"],
      },
      fontSize: {
        micro: ["12px", { letterSpacing: "0.08em" }],
        sm: ["14px", {}],
        base: ["16px", {}],
        lg: ["20px", {}],
        xl: ["24px", {}],
        "2xl": ["32px", {}],
        "3xl": ["44px", {}],
      },
      borderRadius: {
        card: "18px",
      },
      boxShadow: {
        glass: "0 1px 2px rgba(11,18,32,0.04), 0 8px 24px rgba(11,18,32,0.06)",
      },
    },
  },
  plugins: [],
};
export default config;
