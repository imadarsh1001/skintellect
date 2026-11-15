import { onScopeDispose, ref, watch, type Ref } from 'vue'

/**
 * Motion helpers for the dealt moments (add-ui-personality-and-motion).
 * Durations are read from the theme's own custom properties so the tokens
 * in frontend/src/assets/index.css stay the single motion source — no
 * component-local raw values.
 */

/** Parse a `--duration-*` custom property into milliseconds ("450ms" or ".45s"). */
export function motionDurationMs(tokenName: string): number {
  if (typeof window === 'undefined') return 0
  const raw = getComputedStyle(document.documentElement).getPropertyValue(tokenName).trim()
  const match = raw.match(/([\d.]+)(m?s)/)
  if (!match) return 0
  const value = Number.parseFloat(match[1])
  return match[2] === 's' ? value * 1000 : value
}

/**
 * Count a figure up to its target over the given duration (ease-out settle,
 * the JS twin of --ease-entry). Counts are text-content changes driven by
 * requestAnimationFrame — not CSS-animated layout. Under prefers-reduced-
 * motion (or a zero duration) the figure renders its final value instantly:
 * state stays correct with zero decorative motion.
 */
export function useCountUp(target: Ref<number | undefined>, durationMs: number): Ref<number | null> {
  const display = ref<number | null>(null)
  let raf = 0

  function run(to: number) {
    cancelAnimationFrame(raf)
    const reduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduced || durationMs <= 0) {
      display.value = to
      return
    }
    const start = performance.now()
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / durationMs)
      const eased = 1 - Math.pow(1 - progress, 3)
      display.value = Math.round(to * eased)
      if (progress < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
  }

  watch(target, (to) => {
    if (to !== undefined) run(to)
  }, { immediate: true })
  onScopeDispose(() => cancelAnimationFrame(raf))
  return display
}
