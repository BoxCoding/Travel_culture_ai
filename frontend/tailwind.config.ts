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
        clay: {
          50: "#fdf6f1",
          100: "#f8e8dc",
          200: "#f0cdb0",
          300: "#e6ac7e",
          400: "#dc8a54",
          500: "#c96a35",
          600: "#a94f26",
          700: "#873c20",
          800: "#6d3220",
          900: "#5a2b1e",
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
        soft: "0 10px 40px -15px rgba(90, 43, 30, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
