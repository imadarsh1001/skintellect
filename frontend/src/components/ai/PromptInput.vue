<script setup lang="ts">
import { ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Loader2, Send } from 'lucide-vue-next'

/**
 * Prompt Input pattern (shadcn-vue AI Elements): auto-growing textarea with
 * Enter-to-send, Shift+Enter for a newline, explicit busy state, and a
 * submit action. Replaces the single-line Input + Send footer.
 */
const props = defineProps<{
  modelValue: string
  busy?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit'): void
}>()

const textarea = ref<HTMLTextAreaElement | null>(null)

function autosize() {
  const el = textarea.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 160)}px`
}

watch(
  () => props.modelValue,
  () => autosize(),
)

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (!props.busy && props.modelValue.trim()) emit('submit')
  }
}

function submit() {
  if (props.busy || !props.modelValue.trim()) return
  emit('submit')
}
</script>

<template>
  <div class="p-3.5 border-t flex items-end gap-2 bg-card">
    <textarea
      ref="textarea"
      :value="modelValue"
      rows="1"
      :placeholder="placeholder ?? 'Ask anything...'"
      :disabled="busy"
      class="flex-grow resize-none rounded-xl border border-input bg-background px-3 py-2.5 text-xs sm:text-sm leading-relaxed focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-60"
      @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      @keydown="onKeydown"
    />
    <Button
      variant="default"
      size="sm"
      class="h-10 px-4 gap-1.5 font-bold cursor-pointer shrink-0"
      :disabled="busy || !modelValue.trim()"
      @click="submit"
    >
      <Loader2 v-if="busy" class="w-4 h-4 animate-spin" />
      <Send v-else class="w-4 h-4" />
      Send
    </Button>
  </div>
</template>
