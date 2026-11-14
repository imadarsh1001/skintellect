<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next'

/**
 * Suggestion pattern (shadcn-vue AI Elements): a one-click prompt chip.
 * Content must come from structured backend fields or curated sample
 * prompts — never scraped out of the assistant's own markdown.
 */
defineProps<{
  suggestion: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', suggestion: string): void
}>()
</script>

<template>
  <button
    type="button"
    class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] text-[11px] font-medium bg-secondary text-foreground hover:bg-accent border border-border transition-colors cursor-pointer disabled:opacity-55 disabled:cursor-not-allowed disabled:pointer-events-none"
    :disabled="disabled"
    @click="emit('select', suggestion)"
  >
    <Sparkles class="w-3 h-3 shrink-0" />
    <span>{{ suggestion }}</span>
  </button>
</template>
