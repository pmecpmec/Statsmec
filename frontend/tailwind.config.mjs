/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#7c3aed',
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        secondary: '#c084fc',
        accent: '#f59e0b',
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
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
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
          '0%, 100%': { boxShadow: '0 0 40px rgba(124, 58, 237, 0.5)' },
          '50%': { boxShadow: '0 0 60px rgba(124, 58, 237, 0.8)' },
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
