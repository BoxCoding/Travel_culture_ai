import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        leaf: {
          50: "#f3faf1",
          100: "#e1f3db",
          200: "#c3e6b9",
          300: "#9dd48c",
          400: "#74bd63",
          500: "#4f9d44",
          600: "#3c7e34",
          700: "#2f632a",
          800: "#274f24",
          900: "#21421f",
        },
        ink: {
          900: "#1f1b17",
          800: "#2b2521",
          700: "#3c342d",
        },
        sand: {
          50: "#faf7f2",
          100: "#f3ece1",
          200: "#e8dcc9",
        },
      },
      fontFamily: {
        serif: ["Georgia", "Cambria", "Times New Roman", "serif"],
      },
      boxShadow: {
        soft: "0 10px 40px -15px rgba(39, 79, 36, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
