<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import type { Product, SkinPersona } from '@/lib/types'
import { fetchProducts, fetchPersonas, savePersona } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import FilterSidebar from '@/components/explore/FilterSidebar.vue'
import ProductGrid from '@/components/explore/ProductGrid.vue'
import PersonaDrawer from '@/components/explore/PersonaDrawer.vue'
import ProductDetailModal from '@/components/explore/ProductDetailModal.vue'
import ProductComparisonMatrix from '@/components/compare/ProductComparisonMatrix.vue'
import IngredientGraph from '@/components/graph/IngredientGraph.vue'
import ResearchCopilot from '@/components/research/ResearchCopilot.vue'
import {
  Sparkles,
  SlidersHorizontal,
  Scale,
  Network,
  LayoutGrid,
  ShieldCheck,
  Star,
  CheckCircle2,
  Database,
  FlaskConical,
  Globe,
  MessageSquare,
} from 'lucide-vue-next'

// State
const activeTab = ref<'explore' | 'compare' | 'graph' | 'copilot'>('explore')
const products = ref<Product[]>([])
const loading = ref(false)
const totalProducts = ref(0)
const comparedProducts = ref<Product[]>([])

// Persona State
const personas = ref<SkinPersona[]>([])
const currentPersona = ref<SkinPersona>({
  id: 'uap',
  name: 'Universal Adult Sensitive & Acne',
  skin_type: 'sensitive',
  concerns: ['Acne', 'Redness'],
  goals: ['Barrier Repair', 'Acne Fighting'],
  exclude_fungal_acne_triggers: true,
  exclude_drying_alcohols: true,
  exclude_fragrance: true,
  custom_exclusions: [],
})
const personaDrawerOpen = ref(false)

// Product Detail Modal State
const selectedProduct = ref<Product | null>(null)
const detailModalOpen = ref(false)

// Comprehensive Filter State
const search = ref('')
const selectedDomain = ref('all')
const selectedCategory = ref('all')
const selectedCountry = ref('all')
const selectedGoal = ref('all')
const priceTier = ref('all')
const fungalSafe = ref(false)
const fragranceFree = ref(false)
const oilFree = ref(false)
const poreFree = ref(false)
const minMatch = ref(0)
const sortBy = ref('composite_desc')

async function loadData() {
  loading.value = true
  try {
    const [prodRes, personaRes] = await Promise.all([
      fetchProducts({
        search: search.value,
        domain: selectedDomain.value !== 'all' ? selectedDomain.value : undefined,
        category: selectedCategory.value !== 'all' ? selectedCategory.value : undefined,
        country: selectedCountry.value !== 'all' ? selectedCountry.value : undefined,
        goal: selectedGoal.value !== 'all' ? selectedGoal.value : undefined,
        price_tier: priceTier.value !== 'all' ? priceTier.value : undefined,
        fungal_safe: fungalSafe.value,
        fragrance_free: fragranceFree.value,
        oil_free: oilFree.value,
        pore_free: poreFree.value,
        min_match: minMatch.value > 0 ? minMatch.value : undefined,
        sort_by: sortBy.value,
        persona_id: currentPersona.value.id,
      }),
      fetchPersonas(),
    ])

    products.value = prodRes.products || []
    totalProducts.value = prodRes.total || 0
    if (personaRes && personaRes.length > 0) {
      personas.value = personaRes
      const defaultP = personaRes.find(p => p.id === 'uap') || personaRes[0]
      if (defaultP && currentPersona.value.id === 'uap') {
        currentPersona.value = defaultP
      }
    }
  } catch (err) {
    console.error('Failed to load initial catalog data', err)
  } finally {
    loading.value = false
  }
}

// Watch filters to reload products
watch([
  search,
  selectedDomain,
  selectedCategory,
  selectedCountry,
  selectedGoal,
  priceTier,
  fungalSafe,
  fragranceFree,
  oilFree,
  poreFree,
  minMatch,
  sortBy,
], () => {
  loadData()
})

function resetFilters() {
  search.value = ''
  selectedDomain.value = 'all'
  selectedCategory.value = 'all'
  selectedCountry.value = 'all'
  selectedGoal.value = 'all'
  priceTier.value = 'all'
  fungalSafe.value = false
  fragranceFree.value = false
  oilFree.value = false
  poreFree.value = false
  minMatch.value = 0
  sortBy.value = 'composite_desc'
}

function quickFilter(type: 'ceramides' | 'fungal' | 'fragrance' | 'oil_free') {
  if (type === 'ceramides') {
    search.value = 'ceramide'
  } else if (type === 'fungal') {
    fungalSafe.value = !fungalSafe.value
  } else if (type === 'fragrance') {
    fragranceFree.value = !fragranceFree.value
  } else if (type === 'oil_free') {
    oilFree.value = !oilFree.value
  }
}

function handleSelectPersona(p: SkinPersona) {
  currentPersona.value = p
  loadData()
}

async function handleSaveCustomPersona(p: SkinPersona) {
  currentPersona.value = p
  try {
    await savePersona(p)
  } catch (e) {
    console.warn('Persona persisted in session state', e)
  }
  loadData()
}

function toggleCompare(prod: Product) {
  const index = comparedProducts.value.findIndex(p => p.id === prod.id)
  if (index >= 0) {
    comparedProducts.value.splice(index, 1)
  } else {
    if (comparedProducts.value.length >= 4) {
      alert('You can compare up to 4 formulations simultaneously.')
      return
    }
    comparedProducts.value.push(prod)
  }
}

function viewDetails(prod: Product) {
  selectedProduct.value = prod
  detailModalOpen.value = true
}

function openCopilot(prod: Product) {
  if (!comparedProducts.value.some(p => p.id === prod.id)) {
    comparedProducts.value.push(prod)
  }
  activeTab.value = 'copilot'
}

function handleCopilotCompare(prods: Product[]) {
  activeTab.value = 'copilot'
}

onMounted(() => {
  loadData()
  const path = window.location.pathname.toLowerCase()
  const hash = window.location.hash.toLowerCase().replace('#', '')
  if (path.includes('research') || hash === 'copilot' || hash === 'research' || hash === 'chat') {
    activeTab.value = 'copilot'
  } else if (path.includes('compare') || hash === 'compare') {
    activeTab.value = 'compare'
  } else if (path.includes('graph') || hash === 'graph') {
    activeTab.value = 'graph'
  } else if (path.includes('study')) {
    activeTab.value = 'explore'
  }
})

watch(activeTab, (tab) => {
  if (window.location.pathname === '/' || window.location.pathname === '') {
    window.location.hash = tab
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground font-sans selection:bg-primary/20 selection:text-primary">
    <!-- Navbar Header -->
    <header class="border-b bg-card/85 backdrop-blur-md sticky top-0 z-40 shadow-xs">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        <!-- Brand Logo & Global Title -->
        <div class="flex items-center gap-3">
          <div class="size-10 rounded-xl bg-gradient-to-tr from-primary to-emerald-600 text-primary-foreground flex items-center justify-center font-black text-xl shadow-md">
            ✨
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-xl font-black tracking-tight text-foreground">Formulation Studio</h1>
              <Badge variant="verified" class="text-[10px] py-0.5 px-2 font-bold uppercase tracking-wider">
                PRO · MULTI-DOMAIN
              </Badge>
            </div>
            <p class="text-[11px] text-muted-foreground hidden sm:block font-medium">
              Universal Skin, Hair, Body & Makeup Formulation Intelligence
            </p>
          </div>
        </div>

        <!-- Workspaces & Persona Control -->
        <div class="flex items-center gap-2 sm:gap-3">
          <nav class="hidden lg:flex items-center gap-1 text-xs text-muted-foreground mr-1">
            <a
              href="/research"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium"
              title="Structured evidence workspace with quote explorer"
            >
              Evidence Workspace
            </a>
            <a
              href="/study"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium"
              title="3-product demonstration and reference study"
            >
              Study Demo
            </a>
            <a
              href="/progress"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium"
              title="Preparation and indexing status"
            >
              Data Progress
            </a>
          </nav>
          <Button
            variant="outline"
            size="sm"
            class="h-9 px-3.5 gap-2 border-primary/30 bg-primary/5 hover:bg-primary/10 text-primary font-semibold rounded-full shadow-xs cursor-pointer"
            @click="personaDrawerOpen = true"
          >
            <SlidersHorizontal class="w-4 h-4 text-primary" />
            <span class="hidden md:inline text-xs">Profile:</span>
            <span class="text-xs truncate max-w-[160px] text-foreground font-bold">
              {{ currentPersona.name }}
            </span>
          </Button>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6">
        <Tabs :model-value="activeTab" @update:model-value="(v: any) => activeTab = String(v) as any">
          <TabsList class="h-11 bg-transparent p-0 gap-8 border-b-0">
            <TabsTrigger
              value="explore"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <LayoutGrid class="w-4 h-4" />
              Catalog & Explore
            </TabsTrigger>

            <TabsTrigger
              value="compare"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <Scale class="w-4 h-4" />
              Compare Matrix
              <span
                v-if="comparedProducts.length > 0"
                class="size-5 rounded-full bg-primary text-primary-foreground text-[10px] flex items-center justify-center font-bold"
              >
                {{ comparedProducts.length }}
              </span>
            </TabsTrigger>

            <TabsTrigger
              value="graph"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <Network class="w-4 h-4" />
              Ingredient Graph
            </TabsTrigger>

            <TabsTrigger
              value="copilot"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <Sparkles class="w-4 h-4 text-primary" />
              Research Copilot
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full flex flex-col gap-6">
      <!-- 1. Catalog & Explore Tab -->
      <div v-show="activeTab === 'explore'" class="flex flex-col gap-5">
        <!-- Multi-Domain Selector Strip -->
        <div class="bg-card p-2.5 rounded-2xl border shadow-2xs flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-1.5 overflow-x-auto">
            <span class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mr-1.5 shrink-0">Domain:</span>
            <button
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer"
              :class="selectedDomain === 'all' ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-muted text-foreground hover:bg-muted/80'"
              @click="selectedDomain = 'all'"
            >
              <span>🌐</span> All Domains
            </button>
            <button
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer"
              :class="selectedDomain === 'skin' ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-muted text-foreground hover:bg-muted/80'"
              @click="selectedDomain = 'skin'"
            >
              <span>🧴</span> Skin (Face)
            </button>
            <button
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer"
              :class="selectedDomain === 'hair' ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-muted text-foreground hover:bg-muted/80'"
              @click="selectedDomain = 'hair'"
            >
              <span>💇</span> Hair & Scalp
            </button>
            <button
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer"
              :class="selectedDomain === 'body' ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-muted text-foreground hover:bg-muted/80'"
              @click="selectedDomain = 'body'"
            >
              <span>🧼</span> Bath & Body
            </button>
            <button
              class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer"
              :class="selectedDomain === 'makeup' ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-muted text-foreground hover:bg-muted/80'"
              @click="selectedDomain = 'makeup'"
            >
              <span>💄</span> Makeup & Complexion
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
            :class="selectedCategory === 'all' ? 'bg-primary text-primary-foreground shadow-xs' : 'bg-card border text-foreground hover:bg-muted'"
            @click="selectedCategory = 'all'"
          >
            All Categories
          </button>
          <button
            v-for="cat in ['Moisturizers', 'Serums', 'Toners', 'Cleansers', 'Sunscreens', 'Body Lotions']"
            :key="cat"
            class="px-3 py-1 rounded-full text-xs font-semibold transition cursor-pointer shrink-0"
            :class="selectedCategory.toLowerCase() === cat.toLowerCase() ? 'bg-primary text-primary-foreground font-bold shadow-xs' : 'bg-card border text-foreground hover:bg-muted'"
            @click="selectedCategory = cat"
          >
            {{ cat === 'Moisturizers' ? '🧴 Moisturizers' : cat === 'Serums' ? '✨ Serums' : cat === 'Toners' ? '💧 Toners' : cat === 'Cleansers' ? '🧼 Cleansers' : cat === 'Sunscreens' ? '☀️ Sunscreens' : '🧴 Body Lotions' }}
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
                :class="search.toLowerCase().includes('ceramide') ? 'bg-primary text-primary-foreground border-primary font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
                @click="quickFilter('ceramides')"
              >
                Barrier Lipids (Ceramides)
              </button>
              <button
                class="text-xs px-3 py-1 rounded-full border transition-all cursor-pointer font-medium"
                :class="fungalSafe ? 'bg-emerald-600 text-white border-emerald-600 font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
                @click="quickFilter('fungal')"
              >
                🍄 Fungal Acne Safe
              </button>
              <button
                class="text-xs px-3 py-1 rounded-full border transition-all cursor-pointer font-medium"
                :class="fragranceFree ? 'bg-blue-600 text-white border-blue-600 font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
                @click="quickFilter('fragrance')"
              >
                🌸 Fragrance-Free
              </button>
              <button
                class="text-xs px-3 py-1 rounded-full border transition-all cursor-pointer font-medium"
                :class="oilFree ? 'bg-purple-600 text-white border-purple-600 font-bold' : 'bg-card text-foreground border-border hover:bg-muted'"
                @click="quickFilter('oil_free')"
              >
                💧 Oil-Free
              </button>
            </div>
          </div>
        </div>

        <!-- Sidebar & Grid Layout -->
        <div class="flex flex-col lg:flex-row gap-6 items-start">
          <FilterSidebar
            :search="search"
            :category="selectedCategory"
            :country="selectedCountry"
            :goal="selectedGoal"
            :price-tier="priceTier"
            :fungal-safe="fungalSafe"
            :fragrance-free="fragranceFree"
            :oil-free="oilFree"
            :pore-free="poreFree"
            :min-match="minMatch"
            :sort-by="sortBy"
            @update:search="(v: string) => search = v"
            @update:category="(v: string) => selectedCategory = v"
            @update:country="(v: string) => selectedCountry = v"
            @update:goal="(v: string) => selectedGoal = v"
            @update:price-tier="(v: string) => priceTier = v"
            @update:fungal-safe="(v: boolean) => fungalSafe = v"
            @update:fragrance-free="(v: boolean) => fragranceFree = v"
            @update:oil-free="(v: boolean) => oilFree = v"
            @update:pore-free="(v: boolean) => poreFree = v"
            @update:min-match="(v: number) => minMatch = v"
            @update:sort-by="(v: string) => sortBy = v"
            @reset="resetFilters"
          />

          <ProductGrid
            :products="products"
            :loading="loading"
            :compared-ids="comparedProducts.map(p => p.id)"
            @toggle-compare="toggleCompare"
            @open-copilot="openCopilot"
            @view-details="viewDetails"
            @reset-filters="resetFilters"
          />
        </div>
      </div>

      <!-- 2. Compare Matrix Tab -->
      <div v-show="activeTab === 'compare'">
        <ProductComparisonMatrix
          :products="comparedProducts"
          @remove="(pid: number) => comparedProducts = comparedProducts.filter(p => p.id !== pid)"
          @clear-all="comparedProducts = []"
          @ask-copilot-compare="handleCopilotCompare"
        />
      </div>

      <!-- 3. Ingredient Graph Tab -->
      <div v-show="activeTab === 'graph'">
        <IngredientGraph />
      </div>

      <!-- 4. Research Copilot Tab -->
      <div v-show="activeTab === 'copilot'">
        <ResearchCopilot
          :active-product-ids="comparedProducts.map(p => p.id)"
          :persona-id="currentPersona.id"
          @view-details="viewDetails"
          @toggle-compare="toggleCompare"
        />
      </div>
    </main>

    <!-- Persona Drawer Modal -->
    <PersonaDrawer
      :open="personaDrawerOpen"
      :current-persona="currentPersona"
      :available-personas="personas"
      @update:open="(val: boolean) => personaDrawerOpen = val"
      @select-persona="handleSelectPersona"
      @save-custom-persona="handleSaveCustomPersona"
    />

    <!-- Deep Product Details Modal -->
    <ProductDetailModal
      :open="detailModalOpen"
      :product="selectedProduct"
      :current-persona="currentPersona"
      :is-compared="selectedProduct ? comparedProducts.some(p => p.id === selectedProduct?.id) : false"
      @update:open="(val: boolean) => detailModalOpen = val"
      @open-copilot="openCopilot"
      @toggle-compare="toggleCompare"
      @select-product="viewDetails"
    />
  </div>
</template>
