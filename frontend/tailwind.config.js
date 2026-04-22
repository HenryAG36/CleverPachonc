/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        lol: {
          bg: '#0a0e1a',
          card: '#1a2035',
          border: '#2d3748',
          gold: '#c89b3c',
          'gold-dark': '#a07830',
          win: '#3b82f6',
          loss: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
