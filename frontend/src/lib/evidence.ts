/**
 * Evidence-variant class strings for locally extended shadcn-vue primitives.
 *
 * Single source of truth kept OUTSIDE the generated files under
 * `components/ui/` (which the shadcn-vue CLI overwrites on re-pull).
 * After any CLI re-pull, re-attach these variants in `badge/badgeVariants`
 * and `button/buttonVariants` by importing and spreading them.
 *
 * Colors resolve through the `--color-evidence-*` token family in
 * `src/assets/index.css` (Console retheme: verdict pairs measured >= 4.5:1
 * on the graphite ground).
 */
export const evidenceBadgeVariants = {
  verified: 'border-evidence-verified/40 bg-evidence-verified-bg text-evidence-verified font-medium',
  source: 'border-evidence-source/40 bg-evidence-source-bg text-evidence-source font-medium',
  unknown: 'border-evidence-unknown/40 bg-evidence-unknown-bg text-evidence-unknown font-medium',
  negative: 'border-evidence-negative/40 bg-evidence-negative-bg text-evidence-negative font-medium',
  mixed: 'border-evidence-mixed/40 bg-evidence-mixed-bg text-evidence-mixed font-medium',
} as const

export const evidenceButtonVariant = 'bg-evidence-verified text-primary-foreground hover:bg-evidence-verified/90' as const
