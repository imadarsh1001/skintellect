/**
 * Evidence-variant class strings for locally extended shadcn-vue primitives.
 *
 * Single source of truth kept OUTSIDE the generated files under
 * `components/ui/` (which the shadcn-vue CLI overwrites on re-pull).
 * After any CLI re-pull, re-attach these variants in `badge/badgeVariants`
 * and `button/buttonVariants` by importing and spreading them.
 *
 * Colors mirror the `evidence.*` token family (see `tailwind.config.js`
 * history / `@theme` block in `src/assets/index.css`).
 */
export const evidenceBadgeVariants = {
  verified: 'border-[#12635a]/20 bg-[#e5f5f2] text-[#12635a] font-medium',
  source: 'border-[#245ba9]/20 bg-[#eaf2ff] text-[#245ba9] font-medium',
  unknown: 'border-[#805309]/20 bg-[#fff4da] text-[#805309] font-medium',
  negative: 'border-[#a63244]/20 bg-[#fff0f2] text-[#a63244] font-medium',
  mixed: 'border-[#6843a8]/20 bg-[#f2edfc] text-[#6843a8] font-medium',
} as const

export const evidenceButtonVariant = 'bg-[#0e6870] text-white hover:bg-[#0c565d]' as const
