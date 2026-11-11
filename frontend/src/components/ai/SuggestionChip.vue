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
    class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-primary/10 text-primary hover:bg-primary/20 border border-primary/25 transition-all cursor-pointer shadow-2xs hover:scale-[1.02] disabled:opacity-50 disabled:pointer-events-none"
    :disabled="disabled"
    @click="emit('select', suggestion)"
  >
    <Sparkles class="w-3 h-3 shrink-0" />
    <span>{{ suggestion }}</span>
  </button>
</template>
