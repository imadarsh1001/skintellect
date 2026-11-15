<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Product, SkinPersona } from '@/lib/types'
import { fetchProduct } from '@/lib/api'
import { ingredientBenefitIcons } from '@/lib/utils'

// A failed local icon just gets out of the way (name/title text carries the
// meaning; there is no substitute glyph).
function hideBrokenIcon(event: Event) {
  ;(event.target as HTMLImageElement).style.display = 'none'
}
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
  Check,
  TriangleAlert,
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
    <DialogContent class="max-w-4xl max-h-[90vh] p-0 overflow-hidden flex flex-col gap-0 rounded-lg bg-card border-border">
      <!-- Top Fixed Header -->
      <div v-if="detailedProduct" class="p-5 border-b border-border bg-muted/20 shrink-0 flex items-start justify-between gap-4">
        <div class="flex items-start gap-4">
          <!-- Icon / Avatar -->
          <div class="size-16 sm:size-20 rounded-lg bg-background border border-border flex items-center justify-center shrink-0 select-none">
            <FlaskConical class="size-8 text-muted-foreground" aria-hidden="true" />
          </div>

          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-2 flex-wrap text-xs">
              <span class="font-medium text-muted-foreground">{{ detailedProduct.brand }}</span>
              <span aria-hidden="true" class="h-2.5 w-px bg-border"></span>
              <span class="text-muted-foreground font-medium">{{ detailedProduct.brand_country || 'International' }}</span>
              <span class="px-2 py-0.5 rounded-md text-[11px] font-medium bg-muted text-foreground">
                {{ detailedProduct.category_display || detailedProduct.category || 'Moisturizer' }}
              </span>
            </div>

            <h2 class="detail-name text-foreground text-lg sm:text-xl leading-tight">
              {{ detailedProduct.name }}
            </h2>

            <div class="flex items-center gap-3 text-xs flex-wrap pt-0.5 text-muted-foreground">
              <span v-if="detailedProduct.rating" class="flex items-center gap-1 font-medium text-foreground">
                <Star class="w-3.5 h-3.5 fill-primary text-foreground" />
                {{ detailedProduct.rating.toFixed(1) }}
                <span class="text-muted-foreground font-normal">({{ detailedProduct.review_count || 0 }} reviews)</span>
              </span>
              <span class="font-medium text-foreground px-2 py-0.5 rounded border border-border bg-background">
                {{ detailedProduct.price_tier || '$$' }}<span class="mx-1.5 inline-block h-2.5 w-px bg-border align-middle" aria-hidden="true"></span>{{ detailedProduct.price_range || '$15-$30' }}
              </span>
              <span v-if="detailedProduct.size" class="font-medium text-muted-foreground">
                {{ detailedProduct.size }}
              </span>
              <span v-if="detailedProduct.routine_step" class="text-foreground font-medium">
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
              class="text-sm px-3 py-1 rounded-lg"
            >
              {{ detailedProduct.persona_match.score }}% Fit
            </Badge>
            <Badge
              v-else-if="detailedProduct.persona_match?.match_status === 'contraindicated'"
              variant="negative"
              class="font-medium text-xs px-2.5 py-1 rounded-lg gap-1"
            >
              <AlertTriangle class="w-3.5 h-3.5" />
              Contraindicated
            </Badge>
            <Badge
              v-else-if="detailedProduct.match_score !== undefined"
              variant="verified"
              class="text-sm px-3 py-1 rounded-lg"
            >
              {{ detailedProduct.match_score }}% Fit
            </Badge>
            <Badge v-else variant="unknown" class="font-medium text-xs px-2.5 py-1 rounded-lg">
              No heuristic fit
            </Badge>
            <div v-if="detailedProduct.composite_score !== undefined" class="text-[11px] text-muted-foreground font-medium mt-1">
              {{ detailedProduct.composite_score }} pts
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs Bar -->
      <Tabs v-model="activeTab" class="flex flex-col flex-1 min-h-0">
        <TabsList class="w-full shrink-0 justify-start rounded-none h-auto bg-card border-b border-border px-5 gap-1 overflow-x-auto p-0">
          <TabsTrigger
            value="safety"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-medium border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-foreground data-[state=active]:border-primary"
          >
            <Shield class="w-4 h-4" />
            Safety &amp; Clinical Fit
          </TabsTrigger>

          <TabsTrigger
            value="ingredients"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-medium border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-foreground data-[state=active]:border-primary"
          >
            <FlaskConical class="w-4 h-4" />
            Full INCI Ingredients
            <span class="text-[11px] opacity-75">({{ detailedProduct?.ingredients?.length || detailedProduct?.names?.length || 0 }})</span>
          </TabsTrigger>

          <TabsTrigger
            value="dupes"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-medium border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-foreground data-[state=active]:border-primary"
          >
            <Scale class="w-4 h-4" />
            Formula Alternatives
            <span class="text-[11px] opacity-75">({{ dupesList.length }})</span>
          </TabsTrigger>

          <TabsTrigger
            value="reviews"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-medium border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-foreground data-[state=active]:border-primary"
          >
            <MessageSquare class="w-4 h-4" />
            Reviews &amp; Experiences
            <span class="text-[11px] opacity-75">({{ detailedProduct?.reviews?.length || 0 }})</span>
          </TabsTrigger>

          <TabsTrigger
            value="raw"
            class="gap-1.5 py-3 px-3.5 border-b-2 rounded-none text-xs font-medium border-transparent text-muted-foreground hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-foreground data-[state=active]:border-primary"
          >
            <FileCode class="w-4 h-4" />
            Raw JSON
          </TabsTrigger>
        </TabsList>

      <!-- Tab Content Area (Scrollable) -->
      <div class="p-6 overflow-y-auto flex-1 min-h-[380px] max-h-[60vh] space-y-6">
        <!-- Loader -->
        <div v-if="loading" class="py-16 text-center flex flex-col items-center justify-center gap-3">
          <Loader2 class="size-8 animate-spin text-foreground" />
          <span class="text-xs font-medium text-muted-foreground">Loading full clinical formulation dossier...</span>
        </div>

        <div v-else-if="detailedProduct" class="space-y-6">
          <!-- 1. SAFETY & CLINICAL FIT TAB -->
          <TabsContent value="safety" class="mt-0 space-y-5 text-xs">
            <!-- Product Description -->
            <div v-if="detailedProduct.description" class="p-4 rounded-lg border bg-muted/20 text-xs text-foreground leading-relaxed">
              <span class="font-medium text-foreground block mb-1 text-[11px]">Product Description</span>
              <p>{{ detailedProduct.description }}</p>
            </div>

            <!-- Provenance & Safety Certifications -->
            <div>
              <h4 class="text-xs font-medium text-muted-foreground mb-2.5">
                Formula Provenance & Safety Certifications
              </h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-if="detailedProduct.formula_status === 'verified_complete'"
                  class="px-2 py-0.5 rounded-[4px] text-xs font-medium bg-evidence-verified-bg text-evidence-verified border border-evidence-verified/40 flex items-center gap-1.5"
                >
                  <ShieldCheck class="w-4 h-4 text-evidence-verified" />
                  Verified INCI List (Complete)
                </span>
                <span
                  v-if="detailedProduct.fungal_acne_safe === 1"
                  class="px-2 py-0.5 rounded-[4px] text-xs font-medium bg-evidence-verified-bg text-evidence-verified border border-evidence-verified/40 "
                >
                  Fungal Acne Safe
                </span>
                <span
                  v-if="detailedProduct.fragrance_free === 1"
                  class="px-2 py-0.5 rounded-[4px] text-xs font-medium bg-evidence-source-bg text-evidence-source border border-evidence-source/40 "
                >
                  Fragrance-Free
                </span>
                <span
                  v-if="detailedProduct.alcohol_free === 1"
                  class="px-2 py-0.5 rounded-[4px] text-xs font-medium bg-evidence-unknown-bg text-evidence-unknown border border-evidence-unknown/40 "
                >
                  Alcohol-Free
                </span>
                <span
                  v-if="detailedProduct.oil_free === 1"
                  class="px-2 py-0.5 rounded-[4px] text-xs font-medium bg-evidence-verified-bg text-evidence-verified border border-evidence-verified/40 "
                >
                  Oil-Free
                </span>
                <span
                  v-if="detailedProduct.silicone_free === 1"
                  class="px-2 py-0.5 rounded-[4px] text-xs font-medium bg-evidence-mixed-bg text-evidence-mixed border border-evidence-mixed/40 "
                >
                  Silicone-Free
                </span>
                <span
                  v-for="b in (detailedProduct.badges || [])"
                  :key="b"
                  class="px-2 py-0.5 rounded-[4px] text-xs font-medium bg-muted text-foreground border"
                >
                  ✓ {{ b }}
                </span>
              </div>
            </div>

            <!-- Actives Functional Grid -->
            <div>
              <h4 class="text-xs font-medium text-muted-foreground mb-2.5">
                Functional Actives Classification
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <!-- Barrier Lipids -->
                <div class="bg-evidence-verified-bg p-4 rounded-lg border border-evidence-verified/40 space-y-2">
                  <span class="text-xs font-medium text-evidence-verified flex items-center gap-1.5">
                    <ShieldCheck class="w-4 h-4 text-evidence-verified" />
                    Barrier & Hydrators
                  </span>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="h in (detailedProduct.analysis?.hydrators || [])"
                      :key="h"
                      class="px-2 py-0.5 bg-background border rounded text-xs font-medium"
                    >
                      {{ h }}
                    </span>
                    <span v-if="!(detailedProduct.analysis?.hydrators || []).length" class="text-muted-foreground italic text-[11px]">
                      No barrier lipids tagged
                    </span>
                  </div>
                </div>

                <!-- Brighteners & Glow -->
                <div class="bg-evidence-source-bg p-4 rounded-lg border border-evidence-source/40 space-y-2">
                  <span class="text-xs font-medium text-evidence-source flex items-center gap-1.5">
                    <Sparkles class="w-4 h-4 text-evidence-source" />
                    Brighteners & Tone
                  </span>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="b in (detailedProduct.analysis?.brighteners || [])"
                      :key="b"
                      class="px-2 py-0.5 bg-background border rounded text-xs font-medium"
                    >
                      {{ b }}
                    </span>
                    <span v-if="!(detailedProduct.analysis?.brighteners || []).length" class="text-muted-foreground italic text-[11px]">
                      No brighteners tagged
                    </span>
                  </div>
                </div>

                <!-- Soothing Agents -->
                <div class="bg-evidence-mixed-bg p-4 rounded-lg border border-evidence-mixed/40 space-y-2">
                  <span class="text-xs font-medium text-evidence-mixed flex items-center gap-1.5">
                    <Leaf class="w-4 h-4 text-evidence-mixed" />
                    Soothing & Anti-Redness
                  </span>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="s in (detailedProduct.analysis?.smoothers || [])"
                      :key="s"
                      class="px-2 py-0.5 bg-background border rounded text-xs font-medium"
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
            <div class="p-4 rounded-lg border bg-muted/20 space-y-1.5">
              <span class="font-medium text-foreground text-xs block">Comedogenic & Pore Clogging Analysis:</span>
              <div v-if="detailedProduct.analysis?.pore_cloggers?.length" class="text-evidence-negative font-medium flex items-center gap-1.5">
                <AlertTriangle class="w-4 h-4 shrink-0" />
                <span>{{ detailedProduct.analysis.pore_cloggers.join(', ') }}</span>
              </div>
              <div v-else class="text-evidence-verified font-medium flex items-center gap-1.5">
                <CheckCircle2 class="w-4 h-4 shrink-0" />
                <span>0 High Pore Cloggers — Non-comedogenic formulation profile</span>
              </div>
            </div>

            <!-- Persona Alignment Breakdown -->
            <div class="p-4 rounded-lg border bg-muted/10 space-y-2">
              <span class="font-medium text-foreground text-xs block">Compatibility with {{ currentPersona.name }}:</span>
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
                  class="w-full h-8 pl-8 pr-3 text-xs rounded-lg border border-input bg-background"
                />
              </div>
            </div>

            <div v-if="filteredIngredients.length === 0" class="p-8 text-center border rounded-lg bg-muted/20 text-xs text-muted-foreground">
              No ingredients matching "{{ ingredientSearch }}".
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="(ing, idx) in filteredIngredients"
                :key="idx"
                class="p-3 rounded-lg border bg-card hover:bg-muted transition-colors flex items-center justify-between text-xs gap-3"
              >
                <div>
                  <div class="font-medium text-foreground flex items-center gap-2">
                    <span class="text-muted-foreground text-[11px] w-5">{{ idx + 1 }}.</span>
                    <span>{{ ing.name || 'Ingredient' }}</span>
                    <!-- The payload's own benefit icons (scripts/fetch_catalog_icons.py
                         serves them locally); a failed load just disappears. -->
                    <span
                      v-if="ingredientBenefitIcons(ing).length > 0"
                      class="inline-flex items-center gap-0.5"
                    >
                      <img
                        v-for="(ic, k) in ingredientBenefitIcons(ing)"
                        :key="k"
                        :src="ic.src"
                        :alt="ic.title"
                        :title="ic.title"
                        class="size-3.5 shrink-0"
                        @error="hideBrokenIcon"
                      />
                    </span>
                  </div>
                  <div class="text-[11px] text-muted-foreground pl-7">
                    {{ ing.function || 'Skin Conditioning Agent · Solvent' }}
                  </div>
                </div>

                <div class="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
                  <span v-if="ing.fungal_trigger" class="px-2 py-0.5 rounded-[4px] text-[11px] font-medium bg-primary text-primary-foreground border border-primary/40">
                    {{ ing.fungal_trigger }}
                  </span>
                  <span v-if="ing.is_pore_clogging || (ing.comedogenic && ing.comedogenic >= 3)" class="px-2 py-0.5 rounded text-[11px] font-medium bg-evidence-negative-bg text-evidence-negative border border-evidence-negative/40">
                    <TriangleAlert class="size-3" aria-hidden="true" /> Pore Clogger
                  </span>
                  <span v-if="ing.comedogenic !== null && ing.comedogenic !== undefined" class="px-2 py-0.5 rounded text-[11px] font-medium border" :class="ing.comedogenic >= 3 ? 'bg-evidence-negative-bg text-evidence-negative border-evidence-negative/40' : 'bg-muted text-foreground border-border'">
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

            <div v-if="!dupesList.length" class="p-8 text-center border rounded-lg bg-muted/20 text-xs text-muted-foreground">
              No formula twins or alternatives currently indexed for this product.
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="d in dupesList"
                :key="d.id"
                class="p-4 rounded-lg border bg-card hover:border-primary/50 transition-colors flex flex-col justify-between gap-3"
              >
                <div>
                  <div class="flex items-start justify-between gap-2">
                    <div>
                      <span class="text-[11px] font-medium text-muted-foreground">{{ d.brand }}</span>
                      <h4 class="font-medium text-foreground text-sm leading-snug">{{ d.name }}</h4>
                    </div>
                    <Badge variant="verified" class="text-xs shrink-0 font-medium">
                      {{ d.similarity }}% Match
                    </Badge>
                  </div>

                  <div class="flex items-center gap-2 mt-2 text-xs">
                    <span class="font-medium text-foreground">{{ d.price_tier }}</span>
                    <span class="text-muted-foreground text-[11px]">({{ d.price_range }})</span>
                    <span v-if="d.is_cheaper" class="px-2 py-0.5 rounded-md text-[11px] font-medium bg-evidence-verified-bg text-evidence-verified ">
                      Budget Twin
                    </span>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  class="w-full text-xs font-medium gap-1.5"
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
                class="px-3 py-1 rounded-full text-xs font-medium transition cursor-pointer border"
                :class="reviewSkinFilter === st.id ? 'bg-primary text-primary-foreground border-primary font-medium' : 'bg-card text-foreground border-border hover:bg-muted'"
                @click="reviewSkinFilter = st.id"
              >
                {{ st.label }} ({{ reviewSkinCounts[st.id] || 0 }})
              </button>
            </div>

            <div v-if="filteredReviews.length === 0" class="p-8 text-center border rounded-lg bg-muted/20 text-xs text-muted-foreground">
              No community reviews found matching {{ reviewSkinFilter }} skin for this formulation.
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="(r, idx) in filteredReviews"
                :key="idx"
                class="p-4 rounded-lg border bg-card space-y-2"
              >
                <div class="flex items-center justify-between border-b border-border pb-2">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-foreground text-xs">{{ r.author || 'Verified User' }}</span>
                    <span class="px-2 py-0.5 rounded-md text-[11px] font-medium bg-muted text-muted-foreground">
                      {{ r.reviewer_skin_type || 'User' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-0.5 text-foreground text-xs">
                    <Star
                      v-for="s in (r.rating || 5)"
                      :key="s"
                      class="size-3 fill-primary text-foreground"
                    />
                  </div>
                </div>

                <p class="text-xs text-foreground leading-relaxed">
                  "{{ r.review_text || '' }}"
                </p>

                <div class="text-[11px] text-muted-foreground pt-1">
                  {{ r.date_posted || 'Recorded review' }}
                </div>
              </div>
            </div>
          </TabsContent>

          <!-- 5. RAW JSON TAB -->
          <TabsContent value="raw" class="mt-0 space-y-2">
            <span class="text-xs text-muted-foreground block">FastAPI Verified Payload:</span>
            <pre class="p-4 rounded-sm bg-muted text-muted-foreground font-mono text-[11px] overflow-x-auto max-h-96 border border-border">{{ JSON.stringify(detailedProduct, null, 2) }}</pre>
          </TabsContent>
        </div>
      </div>
      </Tabs>

      <!-- Bottom Fixed Action Footer -->
      <div v-if="detailedProduct" class="p-4 border-t border-border bg-muted/20 shrink-0 flex items-center justify-between gap-3">
        <div>
          <a
            v-if="detailedProduct.url"
            :href="detailedProduct.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-xs font-medium text-muted-foreground hover:text-foreground flex items-center gap-1.5 transition-colors"
          >
            <span>View Source Dossier</span>
            <ExternalLink class="w-3.5 h-3.5" />
          </a>
        </div>

        <div class="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            class="h-9 px-3 text-xs gap-1.5 font-medium"
            @click="emits('toggle-compare', detailedProduct)"
          >
            <Scale class="w-3.5 h-3.5" />
            {{ isCompared ? 'Remove from Compare' : 'Add to Compare' }}
          </Button>

          <Button
            variant="default"
            size="sm"
            class="h-9 px-4 text-xs gap-1.5 font-medium"
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

<style scoped>
.detail-name {
  overflow-wrap: break-word;
  min-width: 0;
}
</style>
