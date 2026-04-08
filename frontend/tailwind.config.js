/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // DC86 Branding / Twitch-Farben
        dc: {
          purple: '#6441A5',
          violet: '#9146FF',
          mint: '#00C8AF',
          dark: '#1F1F23',
          darker: '#0E0E10',
          gray: '#3A3A44',
          light: '#EFEFF1',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
