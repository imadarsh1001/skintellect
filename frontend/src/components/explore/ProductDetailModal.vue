<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Product, SkinPersona } from '@/lib/types'
import { fetchProduct } from '@/lib/api'
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Star,
  Sparkles,
  Scale,
  Search,
  CheckCircle2,
  X,
  ExternalLink,
  Loader2,
  Droplets,
  Layers,
  Leaf,
  Shield,
  MessageSquare,
  FileCode,
  Flame,
  FlaskConical,
} from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  product: Product | null
  currentPersona: SkinPersona
  isCompared: boolean
}>()

const emits = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'open-copilot', prod: Product): void
  (e: 'toggle-compare', prod: Product): void
  (e: 'select-product', prod: Product): void
}>()

const activeTab = ref<string>('safety')
const loading = ref(false)
const detailedProduct = ref<any | null>(null)
const ingredientSearch = ref('')
const reviewSkinFilter = ref('all')

async function loadDetails() {
  if (!props.product?.id) return
  loading.value = true
  detailedProduct.value = { ...props.product }
  try {
    const full = await fetchProduct(props.product.id, props.currentPersona.id)
    detailedProduct.value = full
  } catch (err) {
    console.warn('Failed to load full product details:', err)
  } finally {
    loading.value = false
  }
}

watch(
  () => props.open,
  (newVal) => {
    if (newVal) {
      activeTab.value = 'safety'
      ingredientSearch.value = ''
      reviewSkinFilter.value = 'all'
      loadDetails()
    }
  },
)

watch(
  () => props.product?.id,
  () => {
    if (props.open) {
      loadDetails()
    }
  },
)

// Filtered Ingredients
const filteredIngredients = computed(() => {
  const p = detailedProduct.value
  if (!p) return []
  const list = p.ingredients && p.ingredients.length > 0
    ? p.ingredients
    : (p.names || []).map((name: string, idx: number) => ({ name, function: 'Skin Conditioning', id: idx }))

  if (!ingredientSearch.value.trim()) return list
  const q = ingredientSearch.value.toLowerCase()
  return list.filter((i: any) =>
    (i.name || '').toLowerCase().includes(q) ||
    (i.function || '').toLowerCase().includes(q)
  )
})

// Dupes and alternatives
const dupesList = computed(() => {
  const p = detailedProduct.value
  if (!p) return []
  return (p.similar_products && p.similar_products.length > 0)
    ? p.similar_products
    : (p.alternatives || [])
})

// Filtered Reviews
const filteredReviews = computed(() => {
  const p = detailedProduct.value
  if (!p || !p.reviews) return []
  if (reviewSkinFilter.value === 'all') return p.reviews
  return p.reviews.filter((r: any) =>
    (r.reviewer_skin_type || '').toLowerCase() === reviewSkinFilter.value.toLowerCase()
  )
})

// Review Skin Type Counts
const reviewSkinCounts = computed(() => {
  const p = detailedProduct.value
  const counts: Record<string, number> = { all: 0, sensitive: 0, oily: 0, dry: 0, combination: 0, normal: 0 }
  if (!p || !p.reviews) return counts
  counts.all = p.reviews.length
  for (const r of p.reviews) {
    const st = (r.reviewer_skin_type || '').toLowerCase()
    if (st in counts) counts[st]++
  }
  return counts
})

function inspectAlternative(alt: any) {
  emits('select-product', alt)
}
</script>

<template>
  <Dialog :open="open" @update:open="(val: boolean) => emits('update:open', val)">
    <DialogContent class="max-w-4xl max-h-[90vh] p-0 overflow-hidden flex flex-col gap-0 rounded-2xl bg-card border-border/80 shadow-2xl">
      <!-- Top Fixed Header -->
      <div v-if="detailedProduct" class="p-5 border-b border-border/60 bg-muted/20 shrink-0 flex items-start justify-between gap-4">
        <div class="flex items-start gap-4">
          <!-- Icon / Avatar -->
          <div class="size-16 sm:size-20 rounded-2xl bg-background border border-border/80 flex items-center justify-center text-3xl shadow-xs shrink-0 select-none">
            🧴
          </div>

          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-2 flex-wrap text-xs">
              <span class="font-extrabold uppercase tracking-wider text-muted-foreground">{{ detailedProduct.brand }}</span>
              <span class="text-muted-foreground font-semibold">·</span>
              <span class="text-muted-foreground font-medium">{{ detailedProduct.brand_country || 'International' }}</span>
              <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-muted text-foreground">
                {{ detailedProduct.category_display || detailedProduct.category || 'Moisturizer' }}
              </span>
            </div>

            <h2 class="font-extrabold text-foreground text-lg sm:text-xl leading-tight">
              {{ detailedProduct.name }}
            </h2>

            <div class="flex items-center gap-3 text-xs flex-wrap pt-0.5 text-muted-foreground">
              <span v-if="detailedProduct.rating" class="flex items-center gap-1 font-bold text-foreground">
                <Star class="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                {{ detailedProduct.rating.toFixed(1) }}
                <span class="text-muted-foreground font-normal">({{ detailedProduct.review_count || 0 }} reviews)</span>
              </span>
              <span class="font-bold text-foreground px-2 py-0.5 rounded border border-border bg-background">
                {{ detailedProduct.price_tier || '$$' }} · {{ detailedProduct.price_range || '$15-$30' }}
              </span>
              <span v-if="detailedProduct.size" class="font-medium text-muted-foreground">
                {{ detailedProduct.size }}
              </span>
              <span v-if="detailedProduct.routine_step" class="text-primary font-semibold">
                {{ detailedProduct.routine_step }}
              </span>
            </div>
          </div>
        </div>

        <!-- Match Score Top Pill -->
        <div class="flex items-center gap-2 shrink-0">
          <div class="text-right">
            <Badge
              v-if="detailedProduct.persona_match?.match_status === 'match'"
              variant="verified"
              class="font-black text-sm px-3 py-1 rounded-xl shadow-xs"
            >
              {{ detailedProduct.persona_match.score }}% Fit
            </Badge>
            <Badge
              v-else-if="detailedProduct.persona_match?.match_status === 'contraindicated'"
              variant="negative"
              class="font-bold text-xs px-2.5 py-1 rounded-xl shadow-xs gap-1"
            >
              <AlertTriangle class="w-3.5 h-3.5" />
              Contraindicated
            </Badge>
            <Badge
              v-else-if="detailedProduct.match_score !== undefined"
              variant="verified"
              class="font-black text-sm px-3 py-1 rounded-xl shadow-xs"
            >
              {{ detailedProduct.match_score }}% Fit
            </Badge>
            <Badge v-else variant="unknown" class="font-bold text-xs px-2.5 py-1 rounded-xl shadow-xs">
              No heuristic fit
            </Badge>
            <div v-if="detailedProduct.composite_score !== undefined" class="text-[10px] text-muted-foreground font-bold mt-1">
              {{ detailedProduct.composite_score }} pts
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs Bar -->
      <Tabs v-model="activeTab" class="flex flex-col flex-1 min-h-0">
        <TabsList class="w-full shrink-0 justify-start rounded-none h-auto bg-card border-b border-border/60 px-5 gap-1 overflow-x-auto p-0">
          <TabsTrigger
            value="safety"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-bold border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-primary"
          >
            <Shield class="w-4 h-4" />
            Safety &amp; Clinical Fit
          </TabsTrigger>

          <TabsTrigger
            value="ingredients"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-bold border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-primary"
          >
            <FlaskConical class="w-4 h-4" />
            Full INCI Ingredients
            <span class="text-[10px] opacity-75">({{ detailedProduct?.ingredients?.length || detailedProduct?.names?.length || 0 }})</span>
          </TabsTrigger>

          <TabsTrigger
            value="dupes"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-bold border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-primary"
          >
            <Scale class="w-4 h-4" />
            Formula Alternatives
            <span class="text-[10px] opacity-75">({{ dupesList.length }})</span>
          </TabsTrigger>

          <TabsTrigger
            value="reviews"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-bold border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-primary"
          >
            <MessageSquare class="w-4 h-4" />
            Reviews &amp; Experiences
            <span class="text-[10px] opacity-75">({{ detailedProduct?.reviews?.length || 0 }})</span>
          </TabsTrigger>

          <TabsTrigger
            value="raw"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-bold border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-primary"
          >
            <FileCode class="w-4 h-4" />
            Raw JSON
          </TabsTrigger>
        </TabsList>

      <!-- Tab Content Area (Scrollable) -->
      <div class="p-6 overflow-y-auto flex-1 min-h-[380px] max-h-[60vh] space-y-6">
        <!-- Loader -->
        <div v-if="loading" class="py-16 text-center flex flex-col items-center justify-center gap-3">
          <Loader2 class="size-8 animate-spin text-primary" />
          <span class="text-xs font-bold text-muted-foreground">Loading full clinical formulation dossier...</span>
        </div>

        <div v-else-if="detailedProduct" class="space-y-6">
          <!-- 1. SAFETY & CLINICAL FIT TAB -->
          <TabsContent value="safety" class="mt-0 space-y-5 text-xs">
            <!-- Product Description -->
            <div v-if="detailedProduct.description" class="p-4 rounded-xl border bg-muted/20 text-xs text-foreground leading-relaxed">
              <span class="font-bold text-foreground block mb-1 uppercase tracking-wider text-[10px]">Product Description</span>
              <p>{{ detailedProduct.description }}</p>
            </div>

            <!-- Provenance & Safety Certifications -->
            <div>
              <h4 class="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2.5">
                Formula Provenance & Safety Certifications
              </h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-if="detailedProduct.formula_status === 'verified_complete'"
                  class="px-3 py-1 rounded-xl text-xs font-bold bg-emerald-50 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 flex items-center gap-1.5"
                >
                  <ShieldCheck class="w-4 h-4 text-emerald-600" />
                  Verified INCI List (Complete)
                </span>
                <span
                  v-if="detailedProduct.fungal_acne_safe === 1"
                  class="px-3 py-1 rounded-xl text-xs font-bold bg-emerald-50 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                >
                  🍄 Fungal Acne Safe
                </span>
                <span
                  v-if="detailedProduct.fragrance_free === 1"
                  class="px-3 py-1 rounded-xl text-xs font-bold bg-blue-50 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
                >
                  🌸 Fragrance-Free
                </span>
                <span
                  v-if="detailedProduct.alcohol_free === 1"
                  class="px-3 py-1 rounded-xl text-xs font-bold bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700"
                >
                  🌿 Alcohol-Free
                </span>
                <span
                  v-if="detailedProduct.oil_free === 1"
                  class="px-3 py-1 rounded-xl text-xs font-bold bg-teal-50 text-teal-800 dark:bg-teal-950 dark:text-teal-300 border border-teal-200 dark:border-teal-800"
                >
                  💧 Oil-Free
                </span>
                <span
                  v-if="detailedProduct.silicone_free === 1"
                  class="px-3 py-1 rounded-xl text-xs font-bold bg-purple-50 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border border-purple-200 dark:border-purple-800"
                >
                  🌿 Silicone-Free
                </span>
                <span
                  v-for="b in (detailedProduct.badges || [])"
                  :key="b"
                  class="px-3 py-1 rounded-xl text-xs font-bold bg-muted text-foreground border"
                >
                  ✓ {{ b }}
                </span>
              </div>
            </div>

            <!-- Actives Functional Grid -->
            <div>
              <h4 class="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2.5">
                Functional Actives Classification
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <!-- Barrier Lipids -->
                <div class="bg-emerald-50/50 dark:bg-emerald-950/20 p-4 rounded-xl border border-emerald-200/60 dark:border-emerald-800/40 space-y-2">
                  <span class="text-xs font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                    <ShieldCheck class="w-4 h-4 text-emerald-600" />
                    Barrier & Hydrators
                  </span>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="h in (detailedProduct.analysis?.hydrators || [])"
                      :key="h"
                      class="px-2 py-0.5 bg-background border rounded text-xs font-semibold"
                    >
                      {{ h }}
                    </span>
                    <span v-if="!(detailedProduct.analysis?.hydrators || []).length" class="text-muted-foreground italic text-[11px]">
                      No barrier lipids tagged
                    </span>
                  </div>
                </div>

                <!-- Brighteners & Glow -->
                <div class="bg-blue-50/50 dark:bg-blue-950/20 p-4 rounded-xl border border-blue-200/60 dark:border-blue-800/40 space-y-2">
                  <span class="text-xs font-bold text-blue-900 dark:text-blue-300 flex items-center gap-1.5">
                    <Sparkles class="w-4 h-4 text-blue-600" />
                    Brighteners & Tone
                  </span>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="b in (detailedProduct.analysis?.brighteners || [])"
                      :key="b"
                      class="px-2 py-0.5 bg-background border rounded text-xs font-semibold"
                    >
                      {{ b }}
                    </span>
                    <span v-if="!(detailedProduct.analysis?.brighteners || []).length" class="text-muted-foreground italic text-[11px]">
                      No brighteners tagged
                    </span>
                  </div>
                </div>

                <!-- Soothing Agents -->
                <div class="bg-purple-50/50 dark:bg-purple-950/20 p-4 rounded-xl border border-purple-200/60 dark:border-purple-800/40 space-y-2">
                  <span class="text-xs font-bold text-purple-900 dark:text-purple-300 flex items-center gap-1.5">
                    <Leaf class="w-4 h-4 text-purple-600" />
                    Soothing & Anti-Redness
                  </span>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="s in (detailedProduct.analysis?.smoothers || [])"
                      :key="s"
                      class="px-2 py-0.5 bg-background border rounded text-xs font-semibold"
                    >
                      {{ s }}
                    </span>
                    <span v-if="!(detailedProduct.analysis?.smoothers || []).length" class="text-muted-foreground italic text-[11px]">
                      No soothing agents tagged
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pore Clogging Comedogenic Profile -->
            <div class="p-4 rounded-xl border bg-muted/20 space-y-1.5">
              <span class="font-bold text-foreground text-xs block">Comedogenic & Pore Clogging Analysis:</span>
              <div v-if="detailedProduct.analysis?.pore_cloggers?.length" class="text-rose-700 dark:text-rose-400 font-bold flex items-center gap-1.5">
                <AlertTriangle class="w-4 h-4 shrink-0" />
                <span>{{ detailedProduct.analysis.pore_cloggers.join(', ') }}</span>
              </div>
              <div v-else class="text-emerald-700 dark:text-emerald-400 font-bold flex items-center gap-1.5">
                <CheckCircle2 class="w-4 h-4 shrink-0" />
                <span>0 High Pore Cloggers — Non-comedogenic formulation profile</span>
              </div>
            </div>

            <!-- Persona Alignment Breakdown -->
            <div class="p-4 rounded-xl border bg-muted/10 space-y-2">
              <span class="font-bold text-foreground text-xs block">Compatibility with {{ currentPersona.name }}:</span>
              <p class="text-muted-foreground leading-relaxed">
                {{ detailedProduct.persona_match?.explanation || detailedProduct.match_reasons?.join('; ') || 'Formulation satisfies active barrier goals without flagged contraindications.' }}
              </p>
            </div>
          </TabsContent>

          <!-- 2. FULL INCI INGREDIENTS TAB -->
          <TabsContent value="ingredients" class="mt-0 space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <span class="text-xs text-muted-foreground font-medium">
                Full INCI list in decreasing concentration order ({{ filteredIngredients.length }} items):
              </span>
              <div class="relative w-full sm:w-64">
                <Search class="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
                <input
                  v-model="ingredientSearch"
                  type="text"
                  placeholder="Filter ingredients..."
                  class="w-full h-8 pl-8 pr-3 text-xs rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>

            <div v-if="filteredIngredients.length === 0" class="p-8 text-center border rounded-xl bg-muted/20 text-xs text-muted-foreground">
              No ingredients matching "{{ ingredientSearch }}".
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="(ing, idx) in filteredIngredients"
                :key="idx"
                class="p-3 rounded-xl border bg-card hover:bg-muted/30 transition-colors flex items-center justify-between text-xs gap-3"
              >
                <div>
                  <div class="font-bold text-foreground flex items-center gap-2">
                    <span class="text-muted-foreground text-[10px] w-5">{{ idx + 1 }}.</span>
                    <span>{{ ing.name || 'Ingredient' }}</span>
                  </div>
                  <div class="text-[11px] text-muted-foreground pl-7">
                    {{ ing.function || 'Skin Conditioning Agent · Solvent' }}
                  </div>
                </div>

                <div class="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
                  <span v-if="ing.fungal_trigger" class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                    🍄 {{ ing.fungal_trigger }}
                  </span>
                  <span v-if="ing.is_pore_clogging || (ing.comedogenic && ing.comedogenic >= 3)" class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                    ⚠️ Pore Clogger
                  </span>
                  <span v-if="ing.comedogenic !== null && ing.comedogenic !== undefined" class="px-2 py-0.5 rounded text-[10px] font-bold border" :class="ing.comedogenic >= 3 ? 'bg-rose-100 text-rose-800 border-rose-200' : 'bg-muted text-foreground border-border'">
                    Comedo: {{ ing.comedogenic }}
                  </span>
                </div>
              </div>
            </div>
          </TabsContent>

          <!-- 3. FORMULA ALTERNATIVES / DUPES TAB -->
          <TabsContent value="dupes" class="mt-0 space-y-4">
            <span class="text-xs text-muted-foreground font-medium block">
              Algorithmic formula alternatives and budget twins sharing high active overlap:
            </span>

            <div v-if="!dupesList.length" class="p-8 text-center border rounded-xl bg-muted/20 text-xs text-muted-foreground">
              No formula twins or alternatives currently indexed for this product.
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="d in dupesList"
                :key="d.id"
                class="p-4 rounded-xl border bg-card hover:border-primary/50 transition-colors flex flex-col justify-between gap-3 shadow-xs"
              >
                <div>
                  <div class="flex items-start justify-between gap-2">
                    <div>
                      <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{{ d.brand }}</span>
                      <h4 class="font-bold text-foreground text-sm leading-snug">{{ d.name }}</h4>
                    </div>
                    <Badge variant="verified" class="text-xs shrink-0 font-extrabold">
                      {{ d.similarity }}% Match
                    </Badge>
                  </div>

                  <div class="flex items-center gap-2 mt-2 text-xs">
                    <span class="font-bold text-foreground">{{ d.price_tier }}</span>
                    <span class="text-muted-foreground text-[11px]">({{ d.price_range }})</span>
                    <span v-if="d.is_cheaper" class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      💰 Budget Twin
                    </span>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  class="w-full text-xs font-semibold gap-1.5"
                  @click="inspectAlternative(d)"
                >
                  <FlaskConical class="w-3.5 h-3.5" />
                  Inspect This Alternative
                </Button>
              </div>
            </div>
          </TabsContent>

          <!-- 4. COMMUNITY REVIEWS TAB -->
          <TabsContent value="reviews" class="mt-0 space-y-4">
            <!-- Review Skin Filter Chips -->
            <div class="flex items-center gap-2 flex-wrap">
              <button
                v-for="st in [
                  { id: 'all', label: 'All Reviews' },
                  { id: 'sensitive', label: 'Sensitive Skin' },
                  { id: 'oily', label: 'Oily Skin' },
                  { id: 'dry', label: 'Dry Skin' },
                  { id: 'combination', label: 'Combination' }
                ]"
                :key="st.id"
                class="px-3 py-1 rounded-full text-xs font-semibold transition cursor-pointer border"
                :class="reviewSkinFilter === st.id ? 'bg-primary text-primary-foreground border-primary font-bold shadow-xs' : 'bg-card text-foreground border-border hover:bg-muted'"
                @click="reviewSkinFilter = st.id"
              >
                {{ st.label }} ({{ reviewSkinCounts[st.id] || 0 }})
              </button>
            </div>

            <div v-if="filteredReviews.length === 0" class="p-8 text-center border rounded-xl bg-muted/20 text-xs text-muted-foreground">
              No community reviews found matching {{ reviewSkinFilter }} skin for this formulation.
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="(r, idx) in filteredReviews"
                :key="idx"
                class="p-4 rounded-xl border bg-card space-y-2 shadow-xs"
              >
                <div class="flex items-center justify-between border-b border-border/40 pb-2">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-foreground text-xs">{{ r.author || 'Verified User' }}</span>
                    <span class="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-muted text-muted-foreground">
                      {{ r.reviewer_skin_type || 'User' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-0.5 text-amber-500 text-xs">
                    <Star
                      v-for="s in (r.rating || 5)"
                      :key="s"
                      class="size-3 fill-amber-400 text-amber-500"
                    />
                  </div>
                </div>

                <p class="text-xs text-foreground leading-relaxed">
                  "{{ r.review_text || '' }}"
                </p>

                <div class="text-[10px] text-muted-foreground pt-1">
                  {{ r.date_posted || 'Recorded review' }}
                </div>
              </div>
            </div>
          </TabsContent>

          <!-- 5. RAW JSON TAB -->
          <TabsContent value="raw" class="mt-0 space-y-2">
            <span class="text-xs text-muted-foreground font-mono block">FastAPI Verified Payload:</span>
            <pre class="p-4 rounded-xl bg-slate-950 text-emerald-400 font-mono text-[11px] overflow-x-auto max-h-96 border border-slate-800">{{ JSON.stringify(detailedProduct, null, 2) }}</pre>
          </TabsContent>
        </div>
      </div>
      </Tabs>

      <!-- Bottom Fixed Action Footer -->
      <div v-if="detailedProduct" class="p-4 border-t border-border/60 bg-muted/20 shrink-0 flex items-center justify-between gap-3">
        <div>
          <a
            v-if="detailedProduct.url"
            :href="detailedProduct.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-xs font-semibold text-muted-foreground hover:text-foreground flex items-center gap-1.5 transition-colors"
          >
            <span>View Source Dossier</span>
            <ExternalLink class="w-3.5 h-3.5" />
          </a>
        </div>

        <div class="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            class="h-9 px-3 text-xs gap-1.5 font-semibold"
            @click="emits('toggle-compare', detailedProduct)"
          >
            <Scale class="w-3.5 h-3.5" />
            {{ isCompared ? 'Remove from Compare' : 'Add to Compare' }}
          </Button>

          <Button
            variant="default"
            size="sm"
            class="h-9 px-4 text-xs gap-1.5 font-bold shadow-xs"
            @click="emits('open-copilot', detailedProduct)"
          >
            <Sparkles class="w-3.5 h-3.5" />
            Ask Copilot About This Formula
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
