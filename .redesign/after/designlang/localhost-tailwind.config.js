// Measured with designlang: https://designlang.app
/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
    colors: {
        primary: {
            '50': 'hsl(40, 92%, 97%)',
            '100': 'hsl(40, 92%, 94%)',
            '200': 'hsl(40, 92%, 86%)',
            '300': 'hsl(40, 92%, 76%)',
            '400': 'hsl(40, 92%, 64%)',
            '500': 'hsl(40, 92%, 50%)',
            '600': 'hsl(40, 92%, 40%)',
            '700': 'hsl(40, 92%, 32%)',
            '800': 'hsl(40, 92%, 24%)',
            '900': 'hsl(40, 92%, 16%)',
            '950': 'hsl(40, 92%, 10%)',
            DEFAULT: '#f7b83e'
        },
        secondary: {
            '50': 'hsl(207, 96%, 97%)',
            '100': 'hsl(207, 96%, 94%)',
            '200': 'hsl(207, 96%, 86%)',
            '300': 'hsl(207, 96%, 76%)',
            '400': 'hsl(207, 96%, 64%)',
            '500': 'hsl(207, 96%, 50%)',
            '600': 'hsl(207, 96%, 40%)',
            '700': 'hsl(207, 96%, 32%)',
            '800': 'hsl(207, 96%, 24%)',
            '900': 'hsl(207, 96%, 16%)',
            '950': 'hsl(207, 96%, 10%)',
            DEFAULT: '#6ebcfc'
        },
        'neutral-50': '#2d3135',
        'neutral-100': '#a1a7ad',
        'neutral-200': '#5e666e',
        'neutral-300': '#20252a',
        'neutral-400': '#1c0e00',
        background: '#0d1013',
        foreground: '#eceff2'
    },
    fontFamily: {
        sans: [
            'Host Grotesk',
            'sans-serif'
        ],
        mono: [
            'Atkinson Hyperlegible Mono',
            'sans-serif'
        ]
    },
    fontSize: {
        '11': [
            '11px',
            {
                lineHeight: '16.5px'
            }
        ],
        '12': [
            '12px',
            {
                lineHeight: '16px'
            }
        ],
        '14': [
            '14px',
            {
                lineHeight: '20px'
            }
        ],
        '16': [
            '16px',
            {
                lineHeight: '24px'
            }
        ],
        '20': [
            '20px',
            {
                lineHeight: '28px',
                letterSpacing: '-0.6px'
            }
        ],
        '30': [
            '30px',
            {
                lineHeight: '36px',
                letterSpacing: '-0.9px'
            }
        ]
    },
    spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px'
    },
    borderRadius: {
        sm: '4px',
        md: '10px'
    },
    boxShadow: {
        none: 'rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgb(236, 239, 242) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px'
    },
    transitionDuration: {
        '150': '0.15s'
    },
    transitionTimingFunction: {
        custom: 'cubic-bezier(0.4, 0, 0.2, 1)'
    },
    container: {
        center: true,
        padding: '24px'
    },
    maxWidth: {
        container: '1280px'
    }
},
  },
};
