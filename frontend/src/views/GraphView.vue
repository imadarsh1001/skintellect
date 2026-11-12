<script setup lang="ts">
import IngredientGraph from '@/components/graph/IngredientGraph.vue'

defineProps<{
  comparedProducts: import('@/lib/types').Product[]
}>()
</script>

<template>
  <IngredientGraph :products="comparedProducts" />
</template>
