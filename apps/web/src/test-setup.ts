import '@testing-library/jest-dom/vitest'

// Silence jsdom's "Not implemented: HTMLCanvasElement" noise from axe-core's
// color-contrast helper (harmless under jsdom — no real rendering happens).
if (typeof HTMLCanvasElement !== 'undefined') {
  HTMLCanvasElement.prototype.getContext = (() => null) as unknown as typeof HTMLCanvasElement.prototype.getContext
}
