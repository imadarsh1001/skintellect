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
      <span class="text-[11px] font-medium text-foreground">Follow the evidence</span>
      <h2 class="text-2xl sm:text-3xl tracking-tight mt-1">Meet the products. Follow the evidence.</h2>
      <p class="text-sm text-muted-foreground mt-1">
        Choose a product, see what reviewers noticed, then inspect the original sources.
      </p>
    </div>

    <!-- Shaped loading: the study's eventual card shape, so layout holds when data lands -->
    <div v-if="loading" class="my-6 flex flex-col gap-4" aria-hidden="true">
      <div class="h-28 rounded-lg border bg-muted/40 animate-pulse" />
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div v-for="i in 2" :key="i" class="h-56 rounded-lg border bg-muted/40 animate-pulse" />
      </div>
    </div>
    <p v-else-if="error" class="text-xs text-evidence-negative font-medium flex items-center gap-1.5" role="alert">
      <AlertTriangle class="w-3.5 h-3.5" /> {{ error }}
      <Button variant="outline" size="sm" class="h-7 text-[11px] ml-2" @click="load">Retry</Button>
    </p>

    <template v-else-if="demo">
      <!-- Overview cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Card class="border-evidence-verified/30 bg-evidence-verified-bg/40">
          <CardContent class="p-4">
            <span class="text-[11px] font-medium text-evidence-verified">Prepared study</span>
            <p class="text-2xl text-evidence-verified">{{ readyCount }} / {{ demo.products.length }}</p>
            <p class="text-xs text-muted-foreground">Products with selected evidence prepared.</p>
          </CardContent>
        </Card>
        <Card class="border-evidence-source/30 bg-evidence-source-bg/40">
          <CardContent class="p-4">
            <span class="text-[11px] font-medium text-evidence-source">Follow the sources</span>
            <p class="text-2xl text-evidence-source">{{ totalReviews }} reviews</p>
            <p class="text-xs text-muted-foreground">Analyzed reviewer experiences with recorded quotes.</p>
          </CardContent>
        </Card>
        <Card class="border-evidence-unknown/30 bg-evidence-unknown-bg/40">
          <CardContent class="p-4">
            <span class="text-[11px] font-medium text-evidence-unknown">Keep the limits visible</span>
            <p class="text-2xl text-evidence-unknown">Lists unverified</p>
            <p class="text-xs text-muted-foreground">Missing text does not establish absence.</p>
          </CardContent>
        </Card>
      </div>

      <!-- Tabs -->
      <div class="flex items-center gap-2 border-b pb-2">
        <button
          v-for="tab in (['products', 'references', 'quality'] as const)"
          :key="tab"
          type="button"
          class="px-3 py-1.5 min-h-8 inline-flex items-center rounded-lg text-xs font-medium capitalize transition cursor-pointer"
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
                <span class="text-[11px] font-medium text-muted-foreground">{{ product.brand }}</span>
                <CardTitle class="text-sm font-medium">{{ product.name }}</CardTitle>
              </div>
              <Badge :variant="product.ready ? 'verified' : 'unknown'" class="text-[11px] shrink-0">
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
              <Button variant="outline" size="sm" class="h-8 text-[11px] gap-1" @click="toggleReviews(product.id)">
                <Loader2 v-if="loadingReviews[product.id]" class="w-3 h-3 animate-spin" />
                <BookOpen v-else class="w-3 h-3" />
                {{ reviewsByProduct[product.id] && reviewsByProduct[product.id] !== 'error' ? 'Hide evidence' : 'Uncover the evidence' }}
              </Button>
              <RouterLink
                :to="`/research?demo=1&query=${encodeURIComponent(demo.example_query ?? 'What stands out in the reviews?')}`"
                class="text-[11px] font-medium text-foreground hover:underline"
              >
                Ask about this evidence
              </RouterLink>
            </div>

            <div v-if="reviewsByProduct[product.id] === 'error'" class="text-[11px] text-evidence-negative font-medium">
              Review evidence for this product could not be loaded.
            </div>

            <div v-else-if="reviewsByProduct[product.id] && reviewsByProduct[product.id] !== 'error'" class="border-t pt-2 flex flex-col gap-2">
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <div
                  v-for="card in buildSummaryModel(reviewsByProduct[product.id] as ReviewInsights).cards.slice(0, 4)"
                  :key="card.aspect"
                  class="p-2 rounded-lg border bg-card"
                >
                  <div class="font-medium text-foreground text-[11px]">{{ card.label }}</div>
                  <div class="text-muted-foreground text-[11px]">{{ card.mentioning }} of {{ card.denominator }}</div>
                </div>
              </div>
              <p v-if="buildSummaryModel(reviewsByProduct[product.id] as ReviewInsights).oneSidedSample" class="text-xs text-muted-foreground italic">
                A one-sided extracted sample does not establish that reviewers agree.
              </p>
              <div class="flex flex-col gap-1.5">
                <div
                  v-for="(obs, idx) in filterObservations(observationsOf(product.id)).slice(0, 4)"
                  :key="(obs.evidence_id ?? idx) as string | number"
                  class="p-2 rounded-lg border bg-card text-[11px] enter-rise-sm stagger-entry"
                  :style="{ '--stagger-i': idx }"
                >
                  <span class="font-medium text-[11px] px-1 py-0.5 rounded bg-muted text-foreground">
                    {{ observationAspect(obs) }}
                  </span>
                  <span class="font-medium px-1 py-0.5 rounded ml-1 text-[11px]"
                    :class="observationSentiment(obs) === 'negative' ? 'bg-evidence-negative-bg text-evidence-negative' : observationSentiment(obs) === 'positive' ? 'bg-evidence-verified-bg text-evidence-verified' : 'bg-muted text-muted-foreground'">
                    {{ observationSentiment(obs) }}
                  </span>
                  <p class="italic text-foreground/90 mt-1">"{{ obs.span || obs.quote }}"</p>
                </div>
              </div>
              <span class="text-[11px] text-muted-foreground">
                Recorded ingredients: {{ product.recorded_ingredients ?? 'not recorded' }} —
                connections also live in the <RouterLink to="/graph" class="text-foreground font-medium hover:underline">Ingredient Graph</RouterLink>.
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
              <CardTitle class="text-sm font-medium">{{ ref.title }}</CardTitle>
              <Badge variant="source" class="text-[11px] shrink-0">{{ ref.source_type?.replace(/_/g, ' ') }}</Badge>
            </div>
            <span class="text-[11px] text-muted-foreground">{{ ref.publisher }}<span class="mx-1.5 inline-block h-2.5 w-px bg-border align-middle" aria-hidden="true"></span>retrieved {{ ref.retrieved_at?.slice(0, 10) }}</span>
          </CardHeader>
          <CardContent class="pb-4 text-xs flex flex-col gap-2">
            <p class="text-foreground leading-relaxed">{{ ref.summary }}</p>
            <p v-if="ref.quote" class="italic text-muted-foreground">"{{ ref.quote }}"</p>
            <p v-if="ref.limitations" class="text-xs text-evidence-unknown">Limitations: {{ ref.limitations }}</p>
            <a v-if="ref.url" :href="ref.url" target="_blank" rel="noopener noreferrer" class="text-foreground font-medium hover:underline w-fit">
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
            <CardTitle class="text-sm font-medium flex items-center gap-2">
              <FlaskConical class="w-4 h-4 text-foreground" /> Retrieval evaluation
            </CardTitle>
          </CardHeader>
          <CardContent class="pt-4 text-xs flex flex-col gap-3">
            <template v-if="retrievalSummary && Object.keys(retrievalSummary).length">
              <div
                v-for="(summary, mode) in retrievalSummary"
                :key="mode"
                class="flex items-center justify-between p-2 rounded-lg border bg-muted/20"
              >
                <span class="font-medium capitalize">{{ mode }}</span>
                <span class="text-[11px] text-muted-foreground">
                  MRR <span class="font-mono">{{ summary.mrr?.toFixed(3) ?? '—' }}</span><span class="mx-1.5 inline-block h-2.5 w-px bg-border align-middle" aria-hidden="true"></span>Recall@3 <span class="font-mono">{{ summary.recall_at_3?.toFixed(3) ?? '—' }}</span>
                </span>
              </div>
            </template>
            <p v-else class="text-muted-foreground italic">No retrieval evaluation has been recorded yet.</p>
            <p v-if="demo.evaluation?.latency?.limitation" class="text-xs text-muted-foreground italic">
              {{ demo.evaluation.latency.limitation }}
            </p>
            <p v-if="latestLatency" class="text-xs text-muted-foreground">Latest measured latency: {{ latestLatency }} ms</p>
            <p class="text-xs text-muted-foreground flex items-center gap-1">
              <ShieldCheck class="w-3 h-3 text-evidence-verified" />
              {{ demo.evaluation_current ? 'Evaluation matches the current prepared data.' : 'Evaluation is stale relative to the prepared data.' }}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2 border-b">
            <CardTitle class="text-sm font-medium flex items-center gap-2">
              <Scale class="w-4 h-4 text-foreground" /> Catalog audit
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
