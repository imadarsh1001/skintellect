<script setup lang="ts">
import { computed } from 'vue'
import type { Product } from '@/lib/types'
import { useExploreQuery } from '@/composables/useExploreQuery'
import FilterSidebar from '@/components/explore/FilterSidebar.vue'
import ProductGrid from '@/components/explore/ProductGrid.vue'
import {
  Database,
  FlaskConical,
  ShieldCheck,
} from 'lucide-vue-next'

const props = defineProps<{
  personaId: string
  comparedProducts: Product[]
}>()

const emits = defineEmits<{
  (e: 'toggle-compare', product: Product): void
  (e: 'open-copilot', product: Product): void
  (e: 'view-details', product: Product): void
}>()

const {
  products,
  loading,
  filters,
  searchInput,
  setFilter,
  resetFilters,
} = useExploreQuery({ personaId: computed(() => props.personaId) })

const comparedIds = computed(() => props.comparedProducts.map(p => p.id))

const DOMAINS = [
  { value: 'all', label: 'All Domains', icon: '🌐' },
  { value: 'skin', label: 'Skin (Face)', icon: '🧴' },
  { value: 'hair', label: 'Hair & Scalp', icon: '💇' },
  { value: 'body', label: 'Bath & Body', icon: '🧼' },
  { value: 'makeup', label: 'Makeup & Complexion', icon: '💄' },
]

const CATEGORIES = ['Moisturizers', 'Serums', 'Toners', 'Cleansers', 'Sunscreens', 'Body Lotions']

const CATEGORY_ICONS: Record<string, string> = {
  Moisturizers: '🧴',
  Serums: '✨',
  Toners: '💧',
  Cleansers: '🧼',
  Sunscreens: '☀️',
  'Body Lotions': '🧴',
}

function toggleQuickFilter(key: 'fungal_safe' | 'fragrance_free' | 'oil_free') {
  setFilter(key, !filters.value[key])
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <!-- Multi-Domain Selector Strip -->
    <div class="bg-card p-2.5 rounded-2xl border shadow-2xs flex items-center justify-between flex-wrap gap-2">
      <div class="flex items-center gap-1.5 overflow-x-auto">
        <span class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mr-1.5 shrink-0">Domain:</span>
        <button
          v-for="domain in DOMAINS"
          :key="domain.value"
          class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer"
          :class="filters.domain === domain.value ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-muted text-foreground hover:bg-muted/80'"
          @click="setFilter('domain', domain.value)"
        >
          <span>{{ domain.icon }}</span> {{ domain.label }}
        </button>
      </div>

      <div class="flex items-center gap-2 text-xs text-muted-foreground font-medium">
        <span class="size-2 rounded-full bg-emerald-500 animate-pulse"></span>
        Cross-Domain Formulation Engine
      </div>
    </div>

    <!-- Quick Category Selector Strip -->
    <div class="flex items-center gap-1.5 overflow-x-auto pb-1">
      <span class="text-[11px] font-bold text-muted-foreground uppercase tracking-wider mr-1 shrink-0">Category:</span>
      <button
        class="px-3 py-1 rounded-full text-xs font-bold transition cursor-pointer shrink-0"
        :class="filters.category === 'all' ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-card border text-foreground hover:bg-muted'"
        @click="setFilter('category', 'all')"
      >
        All Categories
      </button>
      <button
        v-for="cat in CATEGORIES"
        :key="cat"
        class="px-3 py-1 rounded-full text-xs font-semibold transition cursor-pointer shrink-0"
        :class="filters.category.toLowerCase() === cat.toLowerCase() ? 'bg-primary text-primary-foreground font-bold shadow-xs' : 'bg-card border text-foreground hover:bg-muted'"
        @click="setFilter('category', cat)"
      >
        {{ CATEGORY_ICONS[cat] }} {{ cat }}
      </button>
    </div>

    <!-- Hero Header -->
    <div class="rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/5 via-card to-card p-6 sm:p-8 shadow-xs relative overflow-hidden">
      <div class="max-w-3xl flex flex-col gap-3 relative z-10">
        <div class="flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-[#12635a] bg-[#e5f5f2] border border-[#12635a]/30 px-2.5 py-0.5 rounded-full">
            <ShieldCheck class="w-3.5 h-3.5" />
            546 Verified Complete Formulas
          </span>
          <span class="text-xs text-muted-foreground font-semibold">·</span>
          <span class="inline-flex items-center gap-1 text-[11px] font-bold text-muted-foreground">
            <Database class="w-3 h-3" />
            2,492 Formulations
          </span>
          <span class="text-xs text-muted-foreground font-semibold">·</span>
          <span class="inline-flex items-center gap-1 text-[11px] font-bold text-muted-foreground">
            <FlaskConical class="w-3 h-3" />
            1,490+ Ingredient Dossiers
          </span>
        </div>

        <h2 class="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
          Universal Cosmetic Chemistry & Formulation Intelligence
        </h2>
        <p class="text-sm text-muted-foreground leading-relaxed">
          Explore 2,492+ formulations across Face, Scalp, Body, and Makeup scored deterministically against your skin profile.
          Zero-tolerance contraindications highlight fungal acne triggers, fragrances, and drying alcohols with verifiable proof.
        </p>

        <!-- Quick Filter Chips -->
        <div class="flex flex-wrap items-center gap-2 pt-2">
          <span class="text-xs font-bold text-muted-foreground mr-1">Quick Actives:</span>
          <button
            class="text-xs px-3 py-1 rounded-full border transition-all cursor-pointer font-medium"
            :class="searchInput.toLowerCase().includes('ceramide') ? 'bg-primary text-primary-foreground border-primary font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
            @click="searchInput = searchInput.toLowerCase().includes('ceramide') ? '' : 'ceramide'"
          >
            Barrier Lipids (Ceramides)
          </button>
          <button
            class="text-xs px-3 py-1 rounded-full border transition-all cursor-pointer font-medium"
            :class="filters.fungal_safe ? 'bg-emerald-600 text-white border-emerald-600 font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
            @click="toggleQuickFilter('fungal_safe')"
          >
            🍄 Fungal Acne Safe
          </button>
          <button
            class="text-xs px-3 py-1 rounded-full border transition-all cursor-pointer font-medium"
            :class="filters.fragrance_free ? 'bg-blue-600 text-white border-blue-600 font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
            @click="toggleQuickFilter('fragrance_free')"
          >
            🌸 Fragrance-Free
          </button>
          <button
            class="text-xs px-3 py-1 rounded-full border transition-all cursor-pointer font-medium"
            :class="filters.oil_free ? 'bg-purple-600 text-white border-purple-600 font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
            @click="toggleQuickFilter('oil_free')"
          >
            💧 Oil-Free
          </button>
        </div>
      </div>
    </div>

    <!-- Sidebar & Grid Layout -->
    <div class="flex flex-col lg:flex-row gap-6 items-start">
      <FilterSidebar
        :search="searchInput"
        :category="filters.category"
        :country="filters.country"
        :goal="filters.goal"
        :price-tier="filters.price_tier"
        :fungal-safe="filters.fungal_safe"
        :fragrance-free="filters.fragrance_free"
        :oil-free="filters.oil_free"
        :pore-free="filters.pore_free"
        :min-match="filters.min_match"
        :sort-by="filters.sort_by"
        @update:search="(v: string) => searchInput = v"
        @update:category="(v: string) => setFilter('category', v)"
        @update:country="(v: string) => setFilter('country', v)"
        @update:goal="(v: string) => setFilter('goal', v)"
        @update:price-tier="(v: string) => setFilter('price_tier', v)"
        @update:fungal-safe="(v: boolean) => setFilter('fungal_safe', v)"
        @update:fragrance-free="(v: boolean) => setFilter('fragrance_free', v)"
        @update:oil-free="(v: boolean) => setFilter('oil_free', v)"
        @update:pore-free="(v: boolean) => setFilter('pore_free', v)"
        @update:min-match="(v: number) => setFilter('min_match', v)"
        @update:sort-by="(v: string) => setFilter('sort_by', v)"
        @reset="resetFilters()"
      />

      <ProductGrid
        :products="products"
        :loading="loading"
        :compared-ids="comparedIds"
        @toggle-compare="(prod: Product) => emits('toggle-compare', prod)"
        @open-copilot="(prod: Product) => emits('open-copilot', prod)"
        @view-details="(prod: Product) => emits('view-details', prod)"
        @reset-filters="resetFilters()"
      />
    </div>
  </div>
</template>
