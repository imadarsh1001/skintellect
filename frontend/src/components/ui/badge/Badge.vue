<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80',
        secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80',
        outline: 'text-foreground',
        verified: 'border-[#12635a]/20 bg-[#e5f5f2] text-[#12635a] font-medium',
        source: 'border-[#245ba9]/20 bg-[#eaf2ff] text-[#245ba9] font-medium',
        unknown: 'border-[#805309]/20 bg-[#fff4da] text-[#805309] font-medium',
        negative: 'border-[#a63244]/20 bg-[#fff0f2] text-[#a63244] font-medium',
        mixed: 'border-[#6843a8]/20 bg-[#f2edfc] text-[#6843a8] font-medium',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

type BadgeVariants = VariantProps<typeof badgeVariants>

interface Props {
  variant?: BadgeVariants['variant']
  class?: HTMLAttributes['class']
}

const props = defineProps<Props>()
</script>

<template>
  <div :class="cn(badgeVariants({ variant }), props.class)">
    <slot />
  </div>
</template>
