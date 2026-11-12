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
  <ResearchCopilot
    :active-product-ids="activeProductIds"
    :persona-id="personaId"
    @view-details="(prod: Product) => emits('view-details', prod)"
    @toggle-compare="(prod: Product) => emits('toggle-compare', prod)"
  />
</template>
