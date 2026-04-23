export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        apple: {
          bg: '#000000',
          card: '#1c1c1e',
          card2: '#2c2c2e',
          card3: '#3a3a3c',
          separator: 'rgba(255,255,255,0.08)',
          blue: '#007AFF',
          green: '#30D158',
          red: '#FF453A',
          yellow: '#FFD60A',
          orange: '#FF9F0A',
          purple: '#BF5AF2',
          text: '#ffffff',
          'text-secondary': 'rgba(255,255,255,0.55)',
          'text-tertiary': 'rgba(255,255,255,0.30)',
        },
      },
      fontFamily: {
        apple: ['-apple-system', 'BlinkMacSystemFont', "'SF Pro Display'", "'SF Pro Text'", 'system-ui', 'sans-serif'],
      },
      backdropBlur: {
        apple: '20px',
      },
    },
  },
  plugins: [],
}
