<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  fetchDemo,
  fetchQuality,
  fetchReferences,
  fetchReviewInsights,
  type DemoReadiness,
  type QualityAudit,
  type ReferenceRecord,
  type ReviewInsights,
} from '@/lib/api'
import { buildSummaryModel, filterObservations, observationAspect, observationSentiment } from '@/lib/evidence-summary'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, BookOpen, FlaskConical, Loader2, Scale, ShieldCheck } from 'lucide-vue-next'

/** Split fold-in of the legacy /study page (author decision 2026-11-09):
 * prepared demo group, references library, quality checks. The dead
 * "Read a label" tab (unregistered /api/research/label route) is retired. */

const demo = ref<DemoReadiness | null>(null)
const references = ref<ReferenceRecord[]>([])
const quality = ref<QualityAudit | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref<'products' | 'references' | 'quality'>('products')

const reviewsByProduct = ref<Record<number, ReviewInsights | 'error'>>({})
const loadingReviews = ref<Record<number, boolean>>({})

async function load() {
  loading.value = true
  error.value = null
  try {
    const [demoRes, refRes, qualityRes] = await Promise.all([
      fetchDemo(),
      fetchReferences(),
      fetchQuality(),
    ])
    demo.value = demoRes
    references.value = refRes.references ?? []
    quality.value = qualityRes
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : String(cause)
  } finally {
    loading.value = false
  }
}

onMounted(load)

const readyCount = computed(() => (demo.value?.products ?? []).filter(p => p.ready).length)
const totalReviews = computed(() =>
  (demo.value?.products ?? []).reduce((sum, p) => sum + (p.reviews?.processed ?? 0), 0),
)

async function toggleReviews(productId: number) {
  if (reviewsByProduct.value[productId] && reviewsByProduct.value[productId] !== 'error') {
    delete reviewsByProduct.value[productId]
    reviewsByProduct.value = { ...reviewsByProduct.value }
    return
  }
  loadingReviews.value = { ...loadingReviews.value, [productId]: true }
  try {
    const data = await fetchReviewInsights(productId)
    reviewsByProduct.value = { ...reviewsByProduct.value, [productId]: data }
  } catch {
    reviewsByProduct.value = { ...reviewsByProduct.value, [productId]: 'error' }
  } finally {
    loadingReviews.value = { ...loadingReviews.value, [productId]: false }
  }
}

function observationsOf(productId: number) {
  const data = reviewsByProduct.value[productId]
  return data && data !== 'error' ? (data.observations ?? []) : []
}

const retrievalSummary = computed(() => demo.value?.evaluation?.retrieval?.summary ?? null)
const latestLatency = computed(() => {
  const measurements = demo.value?.evaluation?.latency?.measurements ?? []
  const last = measurements[measurements.length - 1]
  return last?.elapsed_ms ?? null
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="border-b pb-4">
      <span class="text-[11px] font-bold uppercase tracking-wider text-primary">Follow the evidence</span>
      <h2 class="text-2xl sm:text-3xl font-black tracking-tight mt-1">Meet the products. Follow the evidence.</h2>
      <p class="text-sm text-muted-foreground mt-1">
        Choose a product, see what reviewers noticed, then inspect the original sources.
      </p>
    </div>

    <Loader2 v-if="loading" class="w-5 h-5 animate-spin text-primary mx-auto my-8" />
    <p v-else-if="error" class="text-xs text-evidence-negative font-semibold flex items-center gap-1.5" role="alert">
      <AlertTriangle class="w-3.5 h-3.5" /> {{ error }}
      <Button variant="outline" size="sm" class="h-7 text-[11px] ml-2" @click="load">Retry</Button>
    </p>

    <template v-else-if="demo">
      <!-- Overview cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Card class="border-evidence-verified/30 bg-evidence-verified-bg/40">
          <CardContent class="p-4">
            <span class="text-[10px] font-bold uppercase tracking-wider text-evidence-verified">Prepared study</span>
            <p class="text-2xl font-black text-evidence-verified">{{ readyCount }} / {{ demo.products.length }}</p>
            <p class="text-[11px] text-muted-foreground">Products with selected evidence prepared.</p>
          </CardContent>
        </Card>
        <Card class="border-evidence-source/30 bg-evidence-source-bg/40">
          <CardContent class="p-4">
            <span class="text-[10px] font-bold uppercase tracking-wider text-evidence-source">Follow the sources</span>
            <p class="text-2xl font-black text-evidence-source">{{ totalReviews }} reviews</p>
            <p class="text-[11px] text-muted-foreground">Analyzed reviewer experiences with recorded quotes.</p>
          </CardContent>
        </Card>
        <Card class="border-evidence-unknown/30 bg-evidence-unknown-bg/40">
          <CardContent class="p-4">
            <span class="text-[10px] font-bold uppercase tracking-wider text-evidence-unknown">Keep the limits visible</span>
            <p class="text-2xl font-black text-evidence-unknown">Lists unverified</p>
            <p class="text-[11px] text-muted-foreground">Missing text does not establish absence.</p>
          </CardContent>
        </Card>
      </div>

      <!-- Tabs -->
      <div class="flex items-center gap-2 border-b pb-2">
        <button
          v-for="tab in (['products', 'references', 'quality'] as const)"
          :key="tab"
          type="button"
          class="px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition cursor-pointer"
          :class="activeTab === tab ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted'"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <!-- Products tab -->
      <div v-if="activeTab === 'products'" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card v-for="product in demo.products" :key="product.id" class="overflow-hidden">
          <CardHeader class="pb-2">
            <div class="flex items-start justify-between gap-2">
              <div>
                <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{{ product.brand }}</span>
                <CardTitle class="text-sm font-bold">{{ product.name }}</CardTitle>
              </div>
              <Badge :variant="product.ready ? 'verified' : 'unknown'" class="text-[10px] shrink-0">
                {{ product.ready ? 'Evidence ready' : 'Preparation pending' }}
              </Badge>
            </div>
          </CardHeader>
          <CardContent class="pb-4 text-xs flex flex-col gap-2.5">
            <div class="flex items-center gap-3 text-muted-foreground text-[11px] flex-wrap">
              <span>Reviews: {{ product.reviews?.processed ?? 0 }} / {{ product.reviews?.eligible ?? 0 }} analyzed</span>
              <span>Passages: {{ product.passages?.indexed ?? 0 }} / {{ product.passages?.eligible ?? 0 }} indexed</span>
            </div>

            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" class="h-7 text-[11px] gap-1" @click="toggleReviews(product.id)">
                <Loader2 v-if="loadingReviews[product.id]" class="w-3 h-3 animate-spin" />
                <BookOpen v-else class="w-3 h-3" />
                {{ reviewsByProduct[product.id] && reviewsByProduct[product.id] !== 'error' ? 'Hide evidence' : 'Uncover the evidence' }}
              </Button>
              <RouterLink
                :to="`/research?demo=1&query=${encodeURIComponent(demo.example_query ?? 'What stands out in the reviews?')}`"
                class="text-[11px] font-bold text-primary hover:underline"
              >
                Ask about this evidence →
              </RouterLink>
            </div>

            <div v-if="reviewsByProduct[product.id] === 'error'" class="text-[11px] text-evidence-negative font-semibold">
              Review evidence for this product could not be loaded.
            </div>

            <div v-else-if="reviewsByProduct[product.id] && reviewsByProduct[product.id] !== 'error'" class="border-t pt-2 flex flex-col gap-2">
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <div
                  v-for="card in buildSummaryModel(reviewsByProduct[product.id] as ReviewInsights).cards.slice(0, 4)"
                  :key="card.aspect"
                  class="p-2 rounded-lg border bg-card"
                >
                  <div class="font-bold text-foreground text-[11px]">{{ card.label }}</div>
                  <div class="text-muted-foreground text-[10px]">{{ card.mentioning }} of {{ card.denominator }}</div>
                </div>
              </div>
              <p v-if="buildSummaryModel(reviewsByProduct[product.id] as ReviewInsights).oneSidedSample" class="text-[10px] text-muted-foreground italic">
                A one-sided extracted sample does not establish that reviewers agree.
              </p>
              <div class="flex flex-col gap-1.5">
                <div
                  v-for="(obs, idx) in filterObservations(observationsOf(product.id)).slice(0, 4)"
                  :key="(obs.evidence_id ?? idx) as string | number"
                  class="p-2 rounded-lg border bg-background/80 text-[11px]"
                >
                  <span class="font-bold uppercase tracking-wider text-[9px] px-1 py-0.5 rounded bg-muted text-foreground">
                    {{ observationAspect(obs) }}
                  </span>
                  <span class="font-bold px-1 py-0.5 rounded ml-1 text-[9px]"
                    :class="observationSentiment(obs) === 'negative' ? 'bg-rose-100 text-rose-800' : observationSentiment(obs) === 'positive' ? 'bg-emerald-100 text-emerald-800' : 'bg-muted text-muted-foreground'">
                    {{ observationSentiment(obs) }}
                  </span>
                  <p class="italic font-serif text-foreground/90 mt-1">"{{ obs.span || obs.quote }}"</p>
                </div>
              </div>
              <span class="text-[10px] text-muted-foreground">
                Recorded ingredients: {{ product.recorded_ingredients ?? 'not recorded' }} —
                connections also live in the <RouterLink to="/graph" class="text-primary font-semibold hover:underline">Ingredient Graph</RouterLink>.
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- References tab -->
      <div v-else-if="activeTab === 'references'" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card v-for="ref in references" :key="ref.evidence_id ?? ref.title" class="overflow-hidden">
          <CardHeader class="pb-2">
            <div class="flex items-center justify-between gap-2">
              <CardTitle class="text-sm font-bold">{{ ref.title }}</CardTitle>
              <Badge variant="source" class="text-[10px] shrink-0">{{ ref.source_type?.replace(/_/g, ' ') }}</Badge>
            </div>
            <span class="text-[10px] text-muted-foreground">{{ ref.publisher }} · retrieved {{ ref.retrieved_at?.slice(0, 10) }}</span>
          </CardHeader>
          <CardContent class="pb-4 text-xs flex flex-col gap-2">
            <p class="text-foreground leading-relaxed">{{ ref.summary }}</p>
            <p v-if="ref.quote" class="italic font-serif text-muted-foreground">"{{ ref.quote }}"</p>
            <p v-if="ref.limitations" class="text-[11px] text-evidence-unknown">Limitations: {{ ref.limitations }}</p>
            <a v-if="ref.url" :href="ref.url" target="_blank" rel="noopener noreferrer" class="text-primary font-bold hover:underline w-fit">
              Open source ↗
            </a>
          </CardContent>
        </Card>
        <p v-if="references.length === 0" class="text-sm text-muted-foreground">No reference notes are indexed yet.</p>
      </div>

      <!-- Quality tab -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader class="pb-2 border-b">
            <CardTitle class="text-sm font-bold flex items-center gap-2">
              <FlaskConical class="w-4 h-4 text-primary" /> Retrieval evaluation
            </CardTitle>
          </CardHeader>
          <CardContent class="pt-4 text-xs flex flex-col gap-3">
            <template v-if="retrievalSummary && Object.keys(retrievalSummary).length">
              <div
                v-for="(summary, mode) in retrievalSummary"
                :key="mode"
                class="flex items-center justify-between p-2 rounded-lg border bg-muted/20"
              >
                <span class="font-bold capitalize">{{ mode }}</span>
                <span class="font-mono text-[11px] text-muted-foreground">
                  MRR {{ summary.mrr?.toFixed(3) ?? '—' }} · Recall@3 {{ summary.recall_at_3?.toFixed(3) ?? '—' }}
                </span>
              </div>
            </template>
            <p v-else class="text-muted-foreground italic">No retrieval evaluation has been recorded yet.</p>
            <p v-if="demo.evaluation?.latency?.limitation" class="text-[11px] text-muted-foreground italic">
              {{ demo.evaluation.latency.limitation }}
            </p>
            <p v-if="latestLatency" class="text-[11px] text-muted-foreground">Latest measured latency: {{ latestLatency }} ms</p>
            <p class="text-[11px] text-muted-foreground flex items-center gap-1">
              <ShieldCheck class="w-3 h-3 text-evidence-verified" />
              {{ demo.evaluation_current ? 'Evaluation matches the current prepared data.' : 'Evaluation is stale relative to the prepared data.' }}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2 border-b">
            <CardTitle class="text-sm font-bold flex items-center gap-2">
              <Scale class="w-4 h-4 text-primary" /> Catalog audit
            </CardTitle>
          </CardHeader>
          <CardContent class="pt-4 text-xs grid grid-cols-2 gap-2">
            <div class="p-2 rounded-lg border bg-muted/20"><span class="text-muted-foreground">Products</span> <strong>{{ quality?.products ?? '—' }}</strong></div>
            <div class="p-2 rounded-lg border bg-muted/20"><span class="text-muted-foreground">Verified formulas</span> <strong>{{ quality?.verified_complete ?? '—' }}</strong></div>
            <div class="p-2 rounded-lg border bg-muted/20"><span class="text-muted-foreground">Reviews</span> <strong>{{ quality?.reviews ?? '—' }}</strong></div>
            <div class="p-2 rounded-lg border bg-muted/20"><span class="text-muted-foreground">Source documents</span> <strong>{{ quality?.source_documents ?? '—' }}</strong></div>
            <div class="p-2 rounded-lg border bg-muted/20"><span class="text-muted-foreground">Truncated reviews</span> <strong>{{ quality?.truncated_reviews ?? '—' }}</strong></div>
            <div class="p-2 rounded-lg border bg-muted/20"><span class="text-muted-foreground">Seed products</span> <strong>{{ quality?.seed_products ?? '—' }}</strong></div>
          </CardContent>
        </Card>
      </div>
    </template>
  </div>
</template>
