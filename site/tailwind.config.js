/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        leaf: {
          50: '#f0f9e8',
          100: '#daf0c6',
          200: '#b8e08f',
          300: '#8ecc5a',
          400: '#6bb536',
          500: '#4a9626',
          600: '#2D5016',
          700: '#244012',
          800: '#1a300e',
          900: '#0f1f08',
        },
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '80ch',
          },
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
