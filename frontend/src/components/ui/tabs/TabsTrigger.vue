<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { TabsTrigger, type TabsTriggerProps, useForwardProps } from 'reka-ui'

const props = defineProps<TabsTriggerProps & { class?: HTMLAttributes['class'] }>()
const forwarded = useForwardProps(props)
</script>

<template>
  <TabsTrigger
    v-bind="forwarded"
    :class="cn('inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3.5 py-1.5 text-sm font-medium feedback active:opacity-80 disabled:pointer-events-none disabled:opacity-55 disabled:cursor-not-allowed data-[state=active]:bg-background data-[state=active]:text-foreground cursor-pointer', props.class)"
  >
    <slot />
  </TabsTrigger>
</template>
