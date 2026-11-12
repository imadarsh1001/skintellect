<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'

/**
 * Message Scroller pattern (shadcn-vue AI Elements, Chat/Message Scroller):
 * owns the scroll position of the conversation. Keeps the user's place when
 * they scroll up; sticks to the newest message while streaming, which the
 * previous hand-rolled container never did.
 */
const props = defineProps<{
  /** Increments whenever content grows (new message or streamed chunk). */
  streamTick?: number
}>()

const container = ref<HTMLElement | null>(null)
const pinned = ref(true)

function onScroll() {
  const el = container.value
  if (!el) return
  pinned.value = el.scrollHeight - el.scrollTop - el.clientHeight < 120
}

async function scrollToBottom(smooth = true) {
  if (!pinned.value) return
  await nextTick()
  const el = container.value
  if (!el) return
  el.scrollTo({ top: el.scrollHeight, behavior: smooth ? 'smooth' : 'auto' })
}

watch(
  () => props.streamTick ?? 0,
  () => scrollToBottom(),
)

defineExpose({
  jumpToBottom: () => {
    pinned.value = true
    scrollToBottom(false)
  },
})
</script>

<template>
  <div
    ref="container"
    class="flex-grow overflow-y-auto p-4 sm:p-5 flex flex-col gap-5"
    @scroll.passive="onScroll"
  >
    <slot />
  </div>
</template>
