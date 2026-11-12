<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { Product } from '@/lib/types'
import { fetchCatalogStats, type CatalogStats } from '@/lib/api'
import { useExploreQuery, DEFAULT_FILTERS } from '@/composables/useExploreQuery'
import FilterSidebar from '@/components/explore/FilterSidebar.vue'
import ProductGrid from '@/components/explore/ProductGrid.vue'
import { Button } from '@/components/ui/button'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import {
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Database,
  FlaskConical,
  Loader2,
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

const PAGE_LIMIT = 36 // matches the backend /api/products default page size

const {
  products,
  total,
  loading,
  error,
  filters,
  page,
  searchInput,
  setFilter,
  setPage,
  resetFilters,
  reload,
} = useExploreQuery({ personaId: computed(() => props.personaId) })

const comparedIds = computed(() => props.comparedProducts.map(p => p.id))

const stats = ref<CatalogStats | null>(null)
const statsLoading = ref(true)

onMounted(async () => {
  try {
    stats.value = await fetchCatalogStats()
  } catch {
    stats.value = null // hero stat row hides; no stale hardcode is shown
  } finally {
    statsLoading.value = false
  }
})

const verifiedCount = computed(() => {
  if (!stats.value) return null
  const complete = (stats.value as Record<string, unknown>)['verified_complete_products']
  return typeof complete === 'number' ? complete : (stats.value.enriched_products ?? null)
})
const verifiedLabel = computed(() =>
  ((stats.value as Record<string, unknown> | null)?.['verified_complete_products']) !== undefined
    ? 'Verified Complete Formulas'
    : 'Enriched Formulations',
)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_LIMIT)))

const pageWindow = computed<(number | '…')[]>(() => {
  const current = page.value
  const last = totalPages.value
  if (last <= 7) return Array.from({ length: last }, (_, i) => i + 1)
  const window: (number | '…')[] = [1]
  const lo = Math.max(2, current - 1)
  const hi = Math.min(last - 1, current + 1)
  if (lo > 2) window.push('…')
  for (let p = lo; p <= hi; p++) window.push(p)
  if (hi < last - 1) window.push('…')
  window.push(last)
  return window
})

const DOMAINS = [
  { value: 'all', label: 'All Domains', icon: '🌐' },
  { value: 'skin', label: 'Skin (Face)', icon: '🧴' },
  { value: 'hair', label: 'Hair & Scalp', icon: '💇' },
  { value: 'body', label: 'Bath & Body', icon: '🧼' },
  { value: 'makeup', label: 'Makeup & Complexion', icon: '💄' },
]

const CATEGORIES = ['Moisturizers', 'Serums', 'Toners', 'Cleansers', 'Sunscreens', 'Body Lotions']

// Highlight the strip item case-insensitively (URL values may vary in case);
// the ToggleGroup item values themselves are the canonical CATEGORIES strings.
const activeCategory = computed(
  () => CATEGORIES.find((c) => c.toLowerCase() === filters.value.category.toLowerCase()) ?? filters.value.category,
)

const QUICK_FILTER_KEYS = ['fungal_safe', 'fragrance_free', 'oil_free'] as const

const activeQuickFilters = computed(() =>
  QUICK_FILTER_KEYS.filter((k) => filters.value[k]).map(String),
)

function onQuickFiltersUpdate(next: unknown) {
  const active = Array.isArray(next) ? next.map(String) : []
  for (const key of QUICK_FILTER_KEYS) setFilter(key, active.includes(key))
}

const CATEGORY_ICONS: Record<string, string> = {
  Moisturizers: '🧴',
  Serums: '✨',
  Toners: '💧',
  Cleansers: '🧼',
  Sunscreens: '☀️',
  'Body Lotions': '🧴',
}

function goToPage(target: number | '…') {
  if (target === '…' || target === page.value) return
  setPage(target)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <!-- Multi-Domain Selector Strip -->
    <div class="bg-card p-2.5 rounded-2xl border shadow-2xs flex items-center justify-between flex-wrap gap-2">
      <div class="flex items-center gap-1.5 overflow-x-auto">
        <span class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mr-1.5 shrink-0">Domain:</span>
        <ToggleGroup
          type="single"
          :model-value="filters.domain"
          :spacing="1.5"
          class="shrink-0"
          @update:model-value="(v: unknown) => setFilter('domain', typeof v === 'string' ? v : 'all')"
        >
          <ToggleGroupItem
            v-for="domain in DOMAINS"
            :key="domain.value"
            :value="domain.value"
            class="h-auto rounded-xl px-3 py-1.5 text-xs font-bold data-[state=on]:bg-primary data-[state=on]:text-primary-foreground data-[state=on]:shadow-xs data-[state=off]:bg-muted data-[state=off]:text-foreground hover:bg-muted/80 hover:text-foreground"
          >
            <span>{{ domain.icon }}</span> {{ domain.label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <div class="flex items-center gap-2 text-xs text-muted-foreground font-medium">
        <span class="size-2 rounded-full bg-emerald-500 animate-pulse"></span>
        Cross-Domain Formulation Engine
      </div>
    </div>

    <!-- Quick Category Selector Strip -->
    <div class="flex items-center gap-1.5 overflow-x-auto pb-1">
      <span class="text-[11px] font-bold text-muted-foreground uppercase tracking-wider mr-1 shrink-0">Category:</span>
      <ToggleGroup
        type="single"
        :model-value="activeCategory"
        :spacing="1.5"
        class="shrink-0"
        @update:model-value="(v: unknown) => setFilter('category', typeof v === 'string' ? v : 'all')"
      >
        <ToggleGroupItem
          value="all"
          class="h-auto rounded-full px-3 py-1 text-xs font-bold data-[state=on]:bg-primary data-[state=on]:text-primary-foreground data-[state=on]:shadow-xs data-[state=off]:bg-card data-[state=off]:text-foreground data-[state=off]:border hover:bg-muted"
        >
          All Categories
        </ToggleGroupItem>
        <ToggleGroupItem
          v-for="cat in CATEGORIES"
          :key="cat"
          :value="cat"
          class="h-auto rounded-full px-3 py-1 text-xs font-semibold data-[state=on]:bg-primary data-[state=on]:text-primary-foreground data-[state=on]:font-bold data-[state=on]:shadow-xs data-[state=off]:bg-card data-[state=off]:text-foreground data-[state=off]:border hover:bg-muted"
        >
          {{ CATEGORY_ICONS[cat] }} {{ cat }}
        </ToggleGroupItem>
      </ToggleGroup>
    </div>

    <!-- Hero Header -->
    <div class="rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/5 via-card to-card p-6 sm:p-8 shadow-xs relative overflow-hidden">
      <div class="max-w-3xl flex flex-col gap-3 relative z-10">
        <div v-if="statsLoading" class="flex items-center gap-2 text-xs text-muted-foreground">
          <Loader2 class="w-3.5 h-3.5 animate-spin" />
          Loading catalog metrics...
        </div>
        <div v-else-if="stats" class="flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-[#12635a] bg-[#e5f5f2] border border-[#12635a]/30 px-2.5 py-0.5 rounded-full">
            <ShieldCheck class="w-3.5 h-3.5" />
            {{ verifiedCount ?? 0 }} {{ verifiedLabel }}
          </span>
          <span class="text-xs text-muted-foreground font-semibold">·</span>
          <span class="inline-flex items-center gap-1 text-[11px] font-bold text-muted-foreground">
            <Database class="w-3 h-3" />
            {{ stats.total_products.toLocaleString() }} Formulations
          </span>
          <span class="text-xs text-muted-foreground font-semibold">·</span>
          <span class="inline-flex items-center gap-1 text-[11px] font-bold text-muted-foreground">
            <FlaskConical class="w-3 h-3" />
            {{ stats.total_ingredients.toLocaleString() }} Ingredient Dossiers
          </span>
        </div>

        <h2 class="text-2xl sm:text-3xl font-black text-foreground tracking-tight">
          Universal Cosmetic Chemistry & Formulation Intelligence
        </h2>
        <p class="text-sm text-muted-foreground leading-relaxed">
          Explore formulations across Face, Scalp, Body, and Makeup scored deterministically against your skin profile.
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
          <ToggleGroup
            type="multiple"
            :model-value="activeQuickFilters"
            :spacing="2"
            @update:model-value="onQuickFiltersUpdate"
          >
            <ToggleGroupItem
              value="fungal_safe"
              class="h-auto rounded-full px-3 py-1 text-xs font-medium border data-[state=off]:bg-card data-[state=off]:text-foreground data-[state=off]:border-border hover:bg-muted data-[state=on]:bg-emerald-600 data-[state=on]:text-white data-[state=on]:border-emerald-600 data-[state=on]:font-bold"
            >
              🍄 Fungal Acne Safe
            </ToggleGroupItem>
            <ToggleGroupItem
              value="fragrance_free"
              class="h-auto rounded-full px-3 py-1 text-xs font-medium border data-[state=off]:bg-card data-[state=off]:text-foreground data-[state=off]:border-border hover:bg-muted data-[state=on]:bg-blue-600 data-[state=on]:text-white data-[state=on]:border-blue-600 data-[state=on]:font-bold"
            >
              🌸 Fragrance-Free
            </ToggleGroupItem>
            <ToggleGroupItem
              value="oil_free"
              class="h-auto rounded-full px-3 py-1 text-xs font-medium border data-[state=off]:bg-card data-[state=off]:text-foreground data-[state=off]:border-border hover:bg-muted data-[state=on]:bg-purple-600 data-[state=on]:text-white data-[state=on]:border-purple-600 data-[state=on]:font-bold"
            >
              💧 Oil-Free
            </ToggleGroupItem>
          </ToggleGroup>
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

      <div class="flex-grow flex flex-col gap-3">
        <!-- API Error State -->
        <div
          v-if="error"
          class="p-4 rounded-xl border border-evidence-negative/30 bg-evidence-negative-bg/60 flex items-start justify-between gap-3"
          role="alert"
        >
          <div class="flex items-start gap-2 text-xs">
            <AlertTriangle class="w-4 h-4 text-evidence-negative shrink-0 mt-0.5" />
            <div>
              <p class="font-bold text-evidence-negative">Couldn't reach the formulation catalog.</p>
              <p class="text-muted-foreground mt-0.5">{{ error }}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" class="h-8 text-xs shrink-0" @click="reload()">
            Retry
          </Button>
        </div>

        <ProductGrid
          :products="products"
          :loading="loading"
          :compared-ids="comparedIds"
          @toggle-compare="(prod: Product) => emits('toggle-compare', prod)"
          @open-copilot="(prod: Product) => emits('open-copilot', prod)"
          @view-details="(prod: Product) => emits('view-details', prod)"
          @reset-filters="resetFilters()"
        />

        <!-- Results count + Pagination -->
        <div v-if="total > 0 && !loading" class="flex flex-col items-center gap-2 pt-2">
          <p class="text-xs text-muted-foreground font-medium">
            Showing {{ products.length }} of {{ total.toLocaleString() }} matching formulations
          </p>
          <nav v-if="totalPages > 1" class="flex items-center gap-1" aria-label="Catalog pages">
            <Button
              variant="outline"
              size="sm"
              class="h-8 w-8 p-0"
              :disabled="page <= 1"
              aria-label="Previous page"
              @click="goToPage(page - 1)"
            >
              <ChevronLeft class="w-4 h-4" />
            </Button>
            <template v-for="(entry, idx) in pageWindow" :key="idx">
              <span v-if="entry === '…'" class="px-1 text-xs text-muted-foreground">…</span>
              <Button
                v-else
                :variant="entry === page ? 'default' : 'outline'"
                size="sm"
                class="h-8 w-8 p-0 text-xs"
                :aria-current="entry === page ? 'page' : undefined"
                @click="goToPage(entry)"
              >
                {{ entry }}
              </Button>
            </template>
            <Button
              variant="outline"
              size="sm"
              class="h-8 w-8 p-0"
              :disabled="page >= totalPages"
              aria-label="Next page"
              @click="goToPage(page + 1)"
            >
              <ChevronRight class="w-4 h-4" />
            </Button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>
