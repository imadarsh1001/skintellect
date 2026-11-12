<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { DialogDescription, type DialogDescriptionProps } from 'reka-ui'

const props = defineProps<DialogDescriptionProps & { class?: HTMLAttributes['class'] }>()
</script>

<template>
  <DialogDescription
    v-bind="props"
    :class="cn('text-sm text-muted-foreground', props.class)"
  >
    <slot />
  </DialogDescription>
</template>
