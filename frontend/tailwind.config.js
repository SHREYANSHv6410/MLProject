/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        neu: {
          bg: {
            light: '#e9eef5',
            dark: '#161922'
          },
          surface: {
            light: '#e9eef5',
            dark: '#1a1e29'
          },
          primary: {
            DEFAULT: '#6366f1',
            hover: '#4f46e5',
            dark: '#818cf8'
          },
          teal: '#0d9488',
          amber: '#d97706',
          rose: '#e11d48'
        }
      },
      boxShadow: {
        'neu-raised-sm': '3px 3px 6px #cbd4e1, -3px -3px 6px #ffffff',
        'neu-raised': '7px 7px 14px #cbd4e1, -7px -7px 14px #ffffff',
        'neu-raised-lg': '12px 12px 24px #cbd4e1, -12px -12px 24px #ffffff',
        'neu-inset': 'inset 3px 3px 6px #cbd4e1, inset -3px -3px 6px #ffffff',
        'neu-inset-deep': 'inset 5px 5px 10px #cbd4e1, inset -5px -5px 10px #ffffff',
        // Dark theme shadows
        'neu-dark-raised-sm': '3px 3px 6px #0e1017, -3px -3px 6px #242938',
        'neu-dark-raised': '7px 7px 14px #0e1017, -7px -7px 14px #242938',
        'neu-dark-raised-lg': '12px 12px 24px #0e1017, -12px -12px 24px #242938',
        'neu-dark-inset': 'inset 3px 3px 6px #0e1017, inset -3px -3px 6px #242938',
        'neu-dark-inset-deep': 'inset 5px 5px 10px #0e1017, inset -5px -5px 10px #242938',
      }
    },
  },
  plugins: [],
}
