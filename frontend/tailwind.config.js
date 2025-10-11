/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        'landingPageDesktop': '1050px',
        'explorerPageDesktop': '1050px',
        'paperDetailsDesktop': '1050px',
      },
      colors: {
        neutral: {
          100: '#f5f2e7',
          150: '#e8e5da',
          200: '#dad7cd',
          300: '#bebcb3',
          400: '#a2a199',
          500: '#86857f',
          600: '#6b6a65',
          700: '#4f4e4b',
          800: '#333331',
          900: '#171717',
        },
        green: 'rgba(22, 104, 52, 0.7)',
        blue: 'rgba(40, 100, 156, 0.7)',
        orange: 'rgba(234, 147, 0, 0.7)',
        red: 'rgba(129, 12, 12, 0.7)',
      },
      fontFamily: {
        'header': ['Space Grotesk', 'sans-serif'],
        'body': ['Space Mono', 'monospace'],
      },
      animation: {
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        }
      },
    },
  },
  plugins: [],
}