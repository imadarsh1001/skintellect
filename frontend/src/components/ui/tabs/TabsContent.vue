<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { TabsContent, type TabsContentProps } from 'reka-ui'

const props = defineProps<TabsContentProps & { class?: HTMLAttributes['class'] }>()
</script>

<template>
  <TabsContent
    :class="cn('mt-2 focus-visible:', props.class)"
    :value="props.value"
  >
    <slot />
  </TabsContent>
</template>
