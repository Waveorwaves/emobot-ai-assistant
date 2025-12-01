/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
      colors: {
        surface: {
          900: '#020617', // Slate 950
          800: '#0f172a', // Slate 900
          700: '#1e293b', // Slate 800
        },
        primary: {
          400: '#22d3ee', // Neon Cyan 400
          500: '#06b6d4', // Neon Cyan 500
          600: '#0891b2', // Neon Cyan 600
        },
        accent: {
          400: '#f472b6', // Hot Pink 400
          500: '#ec4899', // Hot Pink 500
          600: '#db2777', // Hot Pink 600
        },
        glass: {
          100: 'rgba(255, 255, 255, 0.1)',
          200: 'rgba(255, 255, 255, 0.2)',
          300: 'rgba(255, 255, 255, 0.3)',
        }
      },
      backgroundImage: {
        'cosmic-gradient': 'linear-gradient(to bottom right, #000000, #050505, #110e1b)',
      }
    },
  },
  plugins: [],
}