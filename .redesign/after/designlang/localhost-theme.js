// React Theme — extracted from http://localhost:5173
// Compatible with: Chakra UI, Stitches, Vanilla Extract, or any CSS-in-JS

/**
 * TypeScript type definition for this theme:
 *
 * interface Theme {
 *   colors: {
    primary: string;
    secondary: string;
    background: string;
    foreground: string;
    neutral50: string;
    neutral100: string;
    neutral200: string;
    neutral300: string;
    neutral400: string;
 *   };
 *   fonts: {
    body: string;
    mono: string;
 *   };
 *   fontSizes: {
    '11': string;
    '12': string;
    '14': string;
    '16': string;
    '20': string;
    '30': string;
 *   };
 *   space: {
    '4': string;
    '8': string;
    '12': string;
    '16': string;
    '20': string;
    '24': string;
    '32': string;
 *   };
 *   radii: {
    sm: string;
    md: string;
 *   };
 *   shadows: {
    none: string;
 *   };
 *   states: {
 *     hover: { opacity: number };
 *     focus: { opacity: number };
 *     active: { opacity: number };
 *     disabled: { opacity: number };
 *   };
 * }
 */

export const theme = {
  "colors": {
    "primary": "#f7b83e",
    "secondary": "#6ebcfc",
    "background": "#0d1013",
    "foreground": "#eceff2",
    "neutral50": "#2d3135",
    "neutral100": "#a1a7ad",
    "neutral200": "#5e666e",
    "neutral300": "#20252a",
    "neutral400": "#1c0e00"
  },
  "fonts": {
    "body": "'Host Grotesk', sans-serif",
    "mono": "'Atkinson Hyperlegible Mono', monospace"
  },
  "fontSizes": {
    "11": "11px",
    "12": "12px",
    "14": "14px",
    "16": "16px",
    "20": "20px",
    "30": "30px"
  },
  "space": {
    "4": "4px",
    "8": "8px",
    "12": "12px",
    "16": "16px",
    "20": "20px",
    "24": "24px",
    "32": "32px"
  },
  "radii": {
    "sm": "4px",
    "md": "10px"
  },
  "shadows": {
    "none": "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgb(236, 239, 242) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px"
  },
  "states": {
    "hover": {
      "opacity": 0.08
    },
    "focus": {
      "opacity": 0.12
    },
    "active": {
      "opacity": 0.16
    },
    "disabled": {
      "opacity": 0.38
    }
  }
};

// MUI v5 theme
export const muiTheme = {
  "palette": {
    "primary": {
      "main": "#f7b83e",
      "light": "hsl(40, 92%, 76%)",
      "dark": "hsl(40, 92%, 46%)"
    },
    "secondary": {
      "main": "#6ebcfc",
      "light": "hsl(207, 96%, 86%)",
      "dark": "hsl(207, 96%, 56%)"
    },
    "background": {
      "default": "#0d1013",
      "paper": "#15191c"
    },
    "text": {
      "primary": "#eceff2",
      "secondary": "#61cb7c"
    }
  },
  "typography": {
    "fontFamily": "'Host Grotesk', sans-serif",
    "h2": {
      "fontSize": "30px",
      "fontWeight": "500",
      "lineHeight": "36px"
    },
    "h3": {
      "fontSize": "20px",
      "fontWeight": "500",
      "lineHeight": "28px"
    },
    "body1": {
      "fontSize": "16px",
      "fontWeight": "400",
      "lineHeight": "24px"
    },
    "body2": {
      "fontSize": "11px",
      "fontWeight": "500",
      "lineHeight": "16.5px"
    }
  },
  "shape": {
    "borderRadius": 10
  },
  "shadows": [
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px",
    "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgb(236, 239, 242) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px"
  ]
};

export default theme;
