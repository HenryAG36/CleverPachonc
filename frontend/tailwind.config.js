export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        zar: {
          bg:    '#0d1117',
          bg2:   '#121929',
          card:  '#161c2d',
          card2: '#1e2745',
          card3: '#263355',
          border: 'rgba(255,255,255,0.07)',
          pink:  '#FF2D6B',
          'pink-light': '#FF5588',
          cyan:  '#00CFDD',
          'cyan-light': '#33DDE8',
          green: '#2ECC71',
          red:   '#FF4757',
          // Chart fills — CVD-validated pair (deutan ΔE > 8 on dark surface).
          // Text next to these always carries a word label, never color alone.
          win:   '#4ADE80',
          loss:  '#E5384C',
          yellow: '#FFD60A',
          orange: '#FF9F0A',
          purple: '#BF5AF2',
          text:  '#ffffff',
          'text-secondary': 'rgba(255,255,255,0.55)',
          'text-tertiary':  'rgba(255,255,255,0.30)',
        },
      },
      fontFamily: {
        zar: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      backdropBlur: {
        zar: '20px',
      },
    },
  },
  plugins: [],
}
