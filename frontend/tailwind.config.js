/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        talinay: {
          DEFAULT: "#1e40af",
          dark: "#1e3a8a",
        },
      },
    },
  },
  plugins: [],
};
