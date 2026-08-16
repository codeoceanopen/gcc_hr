// frappe-ui ships raw .ts/.vue source, not built .d.ts files, and its
// package.json "exports" map points "types" straight at that source. That
// means vue-tsc doesn't just check our code -- it walks frappe-ui's entire
// internal module graph and surfaces that package's own internal type
// errors as if they were ours.
//
// A plain `declare module 'frappe-ui'` doesn't help: TS prefers the real,
// resolvable module over an ambient declaration whenever one exists. The
// tsconfig `paths` mapping (see tsconfig.json) redirects the "frappe-ui"
// specifier to this file instead, so this becomes the only definition TS
// ever sees for it. Vite/Rollup are unaffected -- they resolve the real
// package for the actual runtime bundle; this only changes what the
// type-checker sees. Same approach qcore's frontend uses for the same
// package, in this same bench.
//
// Add exports here as new frappe-ui components/composables are used.
export const toast: any
export const Dialog: any
export const Dialogs: any
export const FrappeUIProvider: any
export const Button: any
export const FormControl: any
export const setConfig: any
export const getConfig: any
export const call: any
export const frappeRequest: any
export const createResource: any
export const createListResource: any
export const createDocumentResource: any
export const FileUploader: any
export const AxisChart: any
export const DonutChart: any
export const ECharts: any
