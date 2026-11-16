import { computed, ref, watch, type Ref } from 'vue'
import { usePreferredReducedMotion, useTransition } from '@vueuse/core'

/**
 * Motion helpers for the dealt moments (add-ui-personality-and-motion).
 * Durations are read from the theme's own custom properties so the tokens
 * in frontend/src/assets/index.css stay the single motion source — no
 * component-local raw values. Reduced-motion comes from @vueuse/core's
 * usePreferredReducedMotion — the one shared probe, never a hand-rolled
 * matchMedia literal.
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
 * Count a figure toward its target, built on @vueuse/core's useTransition.
 * Ledger semantics: the tween always starts from the previously displayed
 * value — a ledger amends, it never resets to zero on a recompute. The
 * first arrival still reveals (0 → value). Reduced motion (or a zero
 * duration) renders the final value instantly. Counts are text-content
 * changes driven by the tween — not CSS-animated layout.
 */
export function useCountUp(target: Ref<number | undefined>, durationMs: number): Ref<number | null> {
  const reduced = usePreferredReducedMotion()
  const source = ref(0)
  const tweened = useTransition(source, {
    duration: computed(() => (reduced.value === 'reduce' ? 0 : durationMs)),
    transition: (progress: number) => 1 - Math.pow(1 - progress, 3),
  })
  watch(target, (to) => {
    if (to !== undefined) source.value = to
  }, { immediate: true })
  return computed(() => (target.value === undefined ? null : Math.round(tweened.value)))
}
