/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Phase 1 Design System Tokens
        'primary-navy': '#0F2B46',
        'primary-blue': '#2563EB',
        'light-blue': '#EFF6FF',
        'background': '#F8FAFC',
        'card-bg': '#FFFFFF',
        'text-primary': '#1E293B',
        'text-secondary': '#64748B',
        'border-color': '#E2E8F0',
        'success': '#16A34A',
        'warning': '#F59E0B',
        'error': '#DC2626',
        // Preserved contextual color scales
        navy: {
          900: '#0A1E31',
          DEFAULT: '#0F2B46',
          800: '#14375A',
          700: '#1A436D',
        },
        primary: {
          DEFAULT: '#2563EB',
          dark: '#1D4ED8',
          light: '#3B82F6',
          50: '#EFF6FF',
          100: '#DBEAFE',
        },
        slate: {
          bg: '#F8FAFC',
          card: '#FFFFFF',
          text: '#1E293B',
          muted: '#64748B',
          border: '#E2E8F0',
        },
        gov: {
          success: '#16A34A',
          'success-light': '#F0FDF4',
          warning: '#F59E0B',
          'warning-light': '#FFF7ED',
          error: '#DC2626',
          'error-light': '#FEF2F2',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'card': '12px',
        'btn': '8px',
        'input': '8px',
        'badge': '9999px',
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(15, 43, 70, 0.05), 0 1px 2px 0 rgba(15, 43, 70, 0.03)',
        'elevated': '0 4px 6px -1px rgba(15, 43, 70, 0.07), 0 2px 4px -1px rgba(15, 43, 70, 0.04)',
        'modal': '0 20px 25px -5px rgba(15, 43, 70, 0.1), 0 10px 10px -5px rgba(15, 43, 70, 0.04)',
      },
    },
  },
  plugins: [],
}
