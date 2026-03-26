/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Background layers
        'bg-base':    '#0D1117',
        'bg-sidebar': '#161B27',
        'bg-card':    '#1C2130',
        'bg-card-hover': '#222840',
        // Borders
        'border-subtle': 'rgba(255,255,255,0.07)',
        // Brand
        primary:  '#3B82F6',
        'primary-dim': 'rgba(59,130,246,0.15)',
        cyan:     '#06B6D4',
        // Status
        success:  '#22C55E',
        warning:  '#EAB308',
        danger:   '#EF4444',
        'danger-dim': 'rgba(239,68,68,0.15)',
        orange:   '#F97316',
        // Text
        'text-primary':   '#F0F4FF',
        'text-secondary': '#9CA3AF',
        'text-muted':     '#4B5563',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        card: '12px',
        pill: '999px',
      },
    },
  },
  plugins: [],
}
