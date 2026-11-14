// Measured with designlang: https://designlang.app
/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
    colors: {
        primary: {
            '50': 'hsl(184, 78%, 97%)',
            '100': 'hsl(184, 78%, 94%)',
            '200': 'hsl(184, 78%, 86%)',
            '300': 'hsl(184, 78%, 76%)',
            '400': 'hsl(184, 78%, 64%)',
            '500': 'hsl(184, 78%, 50%)',
            '600': 'hsl(184, 78%, 40%)',
            '700': 'hsl(184, 78%, 32%)',
            '800': 'hsl(184, 78%, 24%)',
            '900': 'hsl(184, 78%, 16%)',
            '950': 'hsl(184, 78%, 10%)',
            DEFAULT: '#0e6b71'
        },
        secondary: {
            '50': 'hsl(214, 47%, 97%)',
            '100': 'hsl(214, 47%, 94%)',
            '200': 'hsl(214, 47%, 86%)',
            '300': 'hsl(214, 47%, 76%)',
            '400': 'hsl(214, 47%, 64%)',
            '500': 'hsl(214, 47%, 50%)',
            '600': 'hsl(214, 47%, 40%)',
            '700': 'hsl(214, 47%, 32%)',
            '800': 'hsl(214, 47%, 24%)',
            '900': 'hsl(214, 47%, 16%)',
            '950': 'hsl(214, 47%, 10%)',
            DEFAULT: '#172940'
        },
        'neutral-50': '#606f85',
        'neutral-100': '#000000',
        background: '#f5f7fa',
        foreground: '#172940'
    },
    fontSize: {
        '10': [
            '10px',
            {
                lineHeight: '15px',
                letterSpacing: '0.5px'
            }
        ],
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
                lineHeight: '28px'
            }
        ],
        '30': [
            '30px',
            {
                lineHeight: '36px',
                letterSpacing: '-0.75px'
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
        md: '8px',
        lg: '16px',
        xl: '24px'
    },
    boxShadow: {
        xs: 'rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.05) 0px 1px 0px 0px',
        sm: 'rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px',
        md: 'rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 4px 6px -1px, rgba(0, 0, 0, 0.1) 0px 2px 4px -2px'
    },
    transitionDuration: {
        '150': '0.15s',
        '200': '0.2s'
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
