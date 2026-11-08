<script setup lang="ts">
import type { Product } from '@/lib/types'
import ProductComparisonMatrix from '@/components/compare/ProductComparisonMatrix.vue'

defineProps<{
  comparedProducts: Product[]
}>()

const emits = defineEmits<{
  (e: 'remove', productId: number): void
  (e: 'clear-all'): void
  (e: 'ask-copilot-compare'): void
}>()
</script>

<template>
  <ProductComparisonMatrix
    :products="comparedProducts"
    @remove="(pid: number) => emits('remove', pid)"
    @clear-all="emits('clear-all')"
    @ask-copilot-compare="emits('ask-copilot-compare')"
  />
</template>
