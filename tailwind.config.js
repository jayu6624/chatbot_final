/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html"],
  theme: {
    extend: {
      colors: {
        chatblack: { 50: "#f2f0eb" },
        left: { 40: "#0d1730" },
      },
    },
  },
  plugins: [],
};
