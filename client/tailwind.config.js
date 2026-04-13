/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#E0E5EC',
        'text-primary': '#3D4852',
        'text-muted': '#6B7280',
        accent: '#6C63FF',
        'accent-teal': '#38B2AC',
      },
      boxShadow: {
        'neu-extruded': '9px 9px 16px rgba(163,177,198,0.6), -9px -9px 16px rgba(255,255,255,0.5)',
        'neu-extruded-hover': '12px 12px 20px rgba(163,177,198,0.7), -12px -12px 20px rgba(255,255,255,0.6)',
        'neu-inset': 'inset 6px 6px 10px rgba(163,177,198,0.6), inset -6px -6px 10px rgba(255,255,255,0.5)',
        'neu-inset-deep': 'inset 10px 10px 20px rgba(163,177,198,0.7), inset -10px -10px 20px rgba(255,255,255,0.6)',
      },
      borderRadius: {
        'neu': '32px',
        'neu-sm': '16px',
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
