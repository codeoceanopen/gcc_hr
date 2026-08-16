import frappeUIPreset from 'frappe-ui/tailwind'

// App-level design tokens (see DESIGN.md) -- a distinct `app.*` color
// namespace and `app-*` radius scale, deliberately NOT overriding
// frappe-ui's own `gray`/`blue`/etc. palette or its `sm`/`md`/`lg` radius
// keys. frappe-ui's own components (Button, FormControl, Dialog, ...) are
// tuned to its own scale; redefining those globally would silently change
// how every imported frappe-ui component looks. Custom app components
// (SectionCard, KpiCard, AppShell, ...) use these `app.*`/`app-*` tokens
// instead, so the two systems coexist without collision.
export default {
  presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,jsx,ts,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        app: {
          bg: '#F8F9FA',
          surface: '#FFFFFF',
          border: '#E2E6EA',
          text: '#171717',
          muted: '#6B7280',
          disabled: '#9CA3AF',
          primary: '#2490EF',
          'primary-hover': '#1B7CD6',
          'primary-surface': '#EAF4FE',
          success: '#28A745',
          'success-surface': '#E9F7EC',
          warning: '#F59E0B',
          'warning-surface': '#FEF3E2',
          danger: '#E5484D',
          'danger-surface': '#FCEAEA',
          info: '#2490EF',
          'info-surface': '#EAF4FE',
        },
      },
      borderRadius: {
        'app-sm': '6px',
        'app-md': '8px',
      },
      // Font family intentionally not overridden here -- frappe-ui's own
      // preset already sets `html { font-family: InterVar, ... }` globally
      // (frappe-ui/tailwind/plugin.js) and bundles the actual Inter
      // variable-font file (frappe-ui/src/fonts/Inter/), so the app is
      // already on Inter everywhere without any extra config.
    },
  },
}
