/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './users/templates/**/*.html',
    './sessions/templates/**/*.html',
    './recommendations/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Custom brand colors
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        // Status colors
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
        },
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
      },
      minHeight: {
        '12': '3rem',
        '16': '4rem',
        '20': '5rem',
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          '"Noto Sans"',
          'sans-serif',
        ],
        mono: [
          '"Fira Code"',
          '"SF Mono"',
          'Monaco',
          'Inconsolata',
          '"Roboto Mono"',
          '"Source Code Pro"',
          'monospace',
        ],
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(0, 0, 0, 0.05)',
        'medium': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'hard': '0 8px 24px rgba(0, 0, 0, 0.15)',
        'inner-soft': 'inset 0 2px 4px rgba(0, 0, 0, 0.05)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'fade-out': 'fadeOut 0.3s ease-in',
        'slide-in-up': 'slideInUp 0.3s ease-out',
        'slide-in-down': 'slideInDown 0.3s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 1s infinite',
        'pulse-gentle': 'pulseGentle 2s infinite',
        'wiggle': 'wiggle 1s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 20%, 53%, 80%, 100%': { transform: 'translate3d(0,0,0)' },
          '40%, 43%': { transform: 'translate3d(0,-15px,0)' },
          '70%': { transform: 'translate3d(0,-7px,0)' },
          '90%': { transform: 'translate3d(0,-2px,0)' },
        },
        pulseGentle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        wiggle: {
          '0%, 7%': { transform: 'rotateZ(0)' },
          '15%': { transform: 'rotateZ(-15deg)' },
          '20%': { transform: 'rotateZ(10deg)' },
          '25%': { transform: 'rotateZ(-10deg)' },
          '30%': { transform: 'rotateZ(6deg)' },
          '35%': { transform: 'rotateZ(-4deg)' },
          '40%, 100%': { transform: 'rotateZ(0)' },
        },
      },
      transitionDuration: {
        '250': '250ms',
        '350': '350ms',
        '400': '400ms',
        '600': '600ms',
        '750': '750ms',
        '900': '900ms',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
      backdropBlur: {
        'xs': '2px',
      },
      screens: {
        'xs': '475px',
        '3xl': '1680px',
        '4xl': '2048px',
      },
    },
  },
  plugins: [
    // Custom plugin for component utilities
    function({ addUtilities, theme }) {
      const newUtilities = {
        // Button variants
        '.btn': {
          '@apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200': {},
        },
        '.btn-sm': {
          '@apply px-3 py-1.5 text-xs': {},
        },
        '.btn-lg': {
          '@apply px-6 py-3 text-base': {},
        },
        '.btn-primary': {
          '@apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500': {},
        },
        '.btn-secondary': {
          '@apply bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500': {},
        },
        '.btn-success': {
          '@apply bg-green-600 text-white hover:bg-green-700 focus:ring-green-500': {},
        },
        '.btn-danger': {
          '@apply bg-red-600 text-white hover:bg-red-700 focus:ring-red-500': {},
        },
        '.btn-warning': {
          '@apply bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500': {},
        },
        '.btn-outline': {
          '@apply bg-transparent border-gray-300 text-gray-700 hover:bg-gray-50': {},
        },
        '.btn-ghost': {
          '@apply bg-transparent border-transparent text-gray-700 hover:bg-gray-100 shadow-none': {},
        },

        // Input styles
        '.input': {
          '@apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200': {},
        },
        '.input-error': {
          '@apply border-red-500 focus:ring-red-500 focus:border-red-500': {},
        },
        '.input-success': {
          '@apply border-green-500 focus:ring-green-500 focus:border-green-500': {},
        },

        // Card styles
        '.card': {
          '@apply bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden': {},
        },
        '.card-hover': {
          '@apply hover:shadow-md transition-shadow duration-200': {},
        },
        '.card-header': {
          '@apply px-6 py-4 border-b border-gray-200 bg-gray-50': {},
        },
        '.card-body': {
          '@apply p-6': {},
        },
        '.card-footer': {
          '@apply px-6 py-4 border-t border-gray-200 bg-gray-50': {},
        },

        // Badge styles
        '.badge': {
          '@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium': {},
        },
        '.badge-primary': {
          '@apply bg-blue-100 text-blue-800': {},
        },
        '.badge-secondary': {
          '@apply bg-gray-100 text-gray-800': {},
        },
        '.badge-success': {
          '@apply bg-green-100 text-green-800': {},
        },
        '.badge-danger': {
          '@apply bg-red-100 text-red-800': {},
        },
        '.badge-warning': {
          '@apply bg-yellow-100 text-yellow-800': {},
        },

        // Modal styles
        '.modal': {
          '@apply fixed inset-0 z-50 hidden': {},
        },
        '.modal.show': {
          '@apply block': {},
        },
        '.modal-backdrop': {
          '@apply absolute inset-0 bg-black bg-opacity-50': {},
        },
        '.modal-content': {
          '@apply relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-auto mt-20 p-6': {},
        },

        // Tooltip styles
        '.tooltip': {
          '@apply absolute z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded shadow-lg pointer-events-none': {},
        },

        // Loading states
        '.skeleton': {
          '@apply animate-pulse bg-gray-200 rounded': {},
        },
        '.skeleton-text': {
          '@apply h-4 bg-gray-200 rounded animate-pulse': {},
        },
        '.skeleton-avatar': {
          '@apply h-10 w-10 bg-gray-200 rounded-full animate-pulse': {},
        },

        // Status indicators
        '.status-indicator': {
          '@apply inline-block w-2 h-2 rounded-full': {},
        },
        '.status-online': {
          '@apply bg-green-400': {},
        },
        '.status-offline': {
          '@apply bg-gray-400': {},
        },
        '.status-busy': {
          '@apply bg-red-400': {},
        },
        '.status-away': {
          '@apply bg-yellow-400': {},
        },

        // Accessibility utilities
        '.sr-only': {
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: '0',
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          border: '0',
        },
        '.not-sr-only': {
          position: 'static',
          width: 'auto',
          height: 'auto',
          padding: '0',
          margin: '0',
          overflow: 'visible',
          clip: 'auto',
          whiteSpace: 'normal',
        },

        // Focus styles for keyboard navigation
        '.keyboard-navigation *:focus': {
          '@apply outline-none ring-2 ring-blue-500 ring-offset-2': {},
        },
      };

      addUtilities(newUtilities);
    },
  ],
  // Safelist classes that might be generated dynamically
  safelist: [
    'bg-blue-100',
    'bg-green-100',
    'bg-yellow-100',
    'bg-red-100',
    'bg-gray-100',
    'text-blue-800',
    'text-green-800',
    'text-yellow-800',
    'text-red-800',
    'text-gray-800',
    'border-blue-500',
    'border-green-500',
    'border-yellow-500',
    'border-red-500',
    'grid-1',
    'grid-2',
    'grid-3',
    'grid-4',
    'translate-x-full',
    'fade-in',
    'slide-in-up',
    'animate-pulse',
  ],
};
