<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { DialogTitle, type DialogTitleProps } from 'reka-ui'

const props = defineProps<DialogTitleProps & { class?: HTMLAttributes['class'] }>()
</script>

<template>
  <DialogTitle
    v-bind="props"
    :class="cn('text-lg font-semibold leading-none tracking-tight text-foreground', props.class)"
  >
    <slot />
  </DialogTitle>
</template>
