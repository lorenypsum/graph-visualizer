/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.html",
    "./index.html",
    "./node_modules/flowbite/**/*.js",
    "./**/*.{js,ts,jsx,tsx,py}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
};