<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { Primitive, type PrimitiveProps } from 'reka-ui'
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-sm text-sm font-medium transition-colors active:opacity-80 disabled:pointer-events-none disabled:opacity-55 disabled:cursor-not-allowed select-none cursor-pointer',
  {
    variants: {
      variant: {
        // Furrow moulded keys: lit inset top edge, shaded inset bottom; active sinks 1px.
        default: 'bg-primary text-primary-foreground hover:bg-primary/90 key-moulded active:translate-y-px',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 key-moulded active:translate-y-px',
        outline: 'border border-border bg-card hover:bg-secondary hover:text-secondary-foreground key-moulded active:translate-y-px',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 key-moulded active:translate-y-px',
        ghost: 'hover:bg-secondary hover:text-secondary-foreground',
        link: 'text-foreground underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2',
        sm: 'h-8 rounded-sm px-3 text-xs',
        lg: 'h-12 rounded-sm px-8',
        icon: 'size-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

type ButtonVariants = VariantProps<typeof buttonVariants>

interface Props extends PrimitiveProps {
  variant?: ButtonVariants['variant']
  size?: ButtonVariants['size']
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
})
</script>

<template>
  <Primitive
    :as="as"
    :as-child="asChild"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <slot />
  </Primitive>
</template>
