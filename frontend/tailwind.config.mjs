/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        stitch: {
          cream: '#fdfbf7',
          paper: '#f5f0e8',
          orange: '#e66b33',
          'orange-soft': 'rgba(230, 107, 51, 0.12)',
          ink: '#1a1a1a',
          muted: '#6b6b6b',
        },
        primary: {
          DEFAULT: '#e66b33',
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#e66b33',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        secondary: '#c084fc',
        accent: '#e66b33',
        cs: {
          green: '#22c55e',
          red: '#ef4444',
          blue: '#3b82f6',
          ct: '#5b98d8',
          t: '#deb352',
        },
        surface: {
          dark: '#0f0f23',
          'dark-alt': '#1a1a2e',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        display: ['var(--font-display)', 'system-ui', 'sans-serif'],
      },
      animation: {
        'glow': 'glow 3s ease-in-out infinite',
        'fade-up': 'fadeUp 0.6s ease forwards',
        'fade-in': 'fadeIn 0.6s ease forwards',
        'slide-left': 'slideLeft 0.6s ease forwards',
        'slide-right': 'slideRight 0.6s ease forwards',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 28px rgba(255, 70, 85, 0.35)' },
          '50%': { boxShadow: '0 0 44px rgba(255, 70, 85, 0.5)' },
        },
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(30px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideLeft: {
          from: { opacity: '0', transform: 'translateX(-30px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        slideRight: {
          from: { opacity: '0', transform: 'translateX(30px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
