<script setup lang="ts">
import type { Product } from '@/lib/types'
import ResearchCopilot from '@/components/research/ResearchCopilot.vue'

defineProps<{
  activeProductIds: number[]
  personaId: string
}>()

const emits = defineEmits<{
  (e: 'view-details', product: Product): void
  (e: 'toggle-compare', product: Product): void
}>()
</script>

<template>
  <!-- The chat view has no visible page title; the sr-only h1 keeps one
       heading level per routed view without adding chrome. -->
  <h1 class="sr-only">Research Copilot</h1>
  <ResearchCopilot
    :active-product-ids="activeProductIds"
    :persona-id="personaId"
    @view-details="(prod: Product) => emits('view-details', prod)"
    @toggle-compare="(prod: Product) => emits('toggle-compare', prod)"
  />
</template>
