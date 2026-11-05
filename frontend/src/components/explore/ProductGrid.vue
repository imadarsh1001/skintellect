<script setup lang="ts">
import type { Product } from '@/lib/types'
import ProductCard from './ProductCard.vue'
import { Inbox, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const props = defineProps<{
  products: Product[]
  loading: boolean
  comparedIds: number[]
}>()

const emits = defineEmits<{
  (e: 'toggle-compare', product: Product): void
  (e: 'open-copilot', product: Product): void
  (e: 'view-details', product: Product): void
  (e: 'reset-filters'): void
}>()
</script>

<template>
  <div class="flex-grow">
    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div
        v-for="i in 6"
        :key="i"
        class="h-72 rounded-xl border bg-card/60 animate-pulse p-5 flex flex-col justify-between"
      >
        <div class="space-y-3">
          <div class="h-4 bg-muted rounded w-1/3"></div>
          <div class="h-6 bg-muted rounded w-3/4"></div>
          <div class="h-4 bg-muted rounded w-1/2"></div>
        </div>
        <div class="h-8 bg-muted rounded w-full"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="products.length === 0"
      class="flex flex-col items-center justify-center py-20 px-4 text-center rounded-xl border border-dashed bg-card/40"
    >
      <Inbox class="w-12 h-12 text-muted-foreground stroke-1 mb-3" />
      <h3 class="text-base font-semibold text-foreground">No matching moisturizers found</h3>
      <p class="text-sm text-muted-foreground max-w-sm mt-1 mb-4">
        Try relaxing sensitivity contraindications or clearing ingredient search filters.
      </p>
      <Button variant="outline" size="sm" @click="emits('reset-filters')">
        Reset All Filters
      </Button>
    </div>

    <!-- Products Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <ProductCard
        v-for="p in products"
        :key="p.id"
        :product="p"
        :is-compared="comparedIds.includes(p.id)"
        @toggle-compare="(prod: Product) => emits('toggle-compare', prod)"
        @open-copilot="(prod: Product) => emits('open-copilot', prod)"
        @view-details="(prod: Product) => emits('view-details', prod)"
      />
    </div>
  </div>
</template>
