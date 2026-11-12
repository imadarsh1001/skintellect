<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  assistantQuery,
  fetchAlternatives,
  fetchDemo,
  fetchEvidence,
  fetchReviewInsights,
  prepareReviews,
  searchInterpret,
  structuredSearch,
  type AlternativesResponse,
  type AssistantResponse,
  type ReviewInsights,
  type SearchIntentPayload,
  type SearchProduct,
  type StructuredSearchResponse,
} from '@/lib/api'
import { aspectLabel, buildSummaryModel, filterObservations, type ObservationLike, type SummaryModel } from '@/lib/evidence-summary'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  AlertTriangle,
  BookOpen,
  ChevronDown,
  FlaskConical,
  Loader2,
  MessageSquare,
  Scale,
  Search,
} from 'lucide-vue-next'

const route = useRoute()

const question = ref(String(route.query.query ?? ''))
const demoScope = ref(route.query.demo === '1')
const interpreting = ref(false)
const answering = ref(false)
const searching = ref(false)
const error = ref<string | null>(null)
const unresolved = ref<string[]>([])
const notice = ref<string | null>(null)

const filters = reactive<Required<Pick<SearchIntentPayload, 'category' | 'domain'>> & {
  required_ingredients: string
  excluded_ingredients: string
  price: string
}>({
  category: 'all',
  domain: 'skin',
  required_ingredients: '',
  excluded_ingredients: '',
  price: '',
})
const filtersVisible = ref(false)
const lastIntent = ref<SearchIntentPayload | null>(null)

const results = ref<StructuredSearchResponse | null>(null)
const answer = ref<AssistantResponse | null>(null)

interface CardExpansion {
  evidence?: { loading: boolean; data?: any; error?: string }
  reviews?: { loading: boolean; data?: ReviewInsights; error?: string; preparing?: boolean }
  alternatives?: { loading: boolean; data?: AlternativesResponse; error?: string }
}
const expansions = reactive<Record<number, CardExpansion>>({})

const DEMO_HINT = 'Search the prepared group only — three products with selected review evidence.'
const demoProductIds = ref<number[]>([])

onMounted(async () => {
  if (demoScope.value || route.query.query) {
    try {
      const readiness = await fetchDemo()
      demoProductIds.value = readiness.product_ids ?? readiness.products.map(p => p.id)
      if (!route.query.query && readiness.example_query && !question.value.trim()) {
        question.value = readiness.example_query
      }
    } catch {
      /* demo readiness is optional context; search still works unscoped */
    }
  }
  if (route.query.query) {
    runAssistant()
  }
})

function scopeIds(): number[] | undefined {
  return demoScope.value && demoProductIds.value.length > 0 ? demoProductIds.value : undefined
}

async function runInterpret() {
  if (!question.value.trim() || interpreting.value) return
  interpreting.value = true
  error.value = null
  try {
    const interpreted = await searchInterpret(question.value.trim())
    const intent = interpreted.intent ?? {}
    filters.category = intent.category ?? 'all'
    filters.domain = (intent.domain as 'skin' | 'hair' | 'body' | 'makeup' | 'all') ?? 'skin'
    filters.required_ingredients = (intent.required_ingredients ?? []).join(', ')
    filters.excluded_ingredients = (intent.excluded_ingredients ?? []).join(', ')
    filters.price = (intent.preferred_price_tiers ?? [])[0] ?? ''
    unresolved.value = intent.unresolved_terms ?? []
    filtersVisible.value = true
    lastIntent.value = intent
    notice.value = interpreted.notice ?? null
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : String(cause)
  } finally {
    interpreting.value = false
  }
}

function buildIntent(): SearchIntentPayload {
  const split = (value: string) => value.split(',').map(s => s.trim()).filter(Boolean)
  const intent: SearchIntentPayload = {
    category: filters.category,
    domain: filters.domain,
    required_ingredients: split(filters.required_ingredients),
    excluded_ingredients: split(filters.excluded_ingredients),
    preferred_price_tiers: filters.price ? [filters.price] : [],
    text: question.value.trim(),
    limit: 10,
  }
  return intent
}

async function runSearch() {
  if (searching.value) return
  searching.value = true
  error.value = null
  answer.value = null
  try {
    const intent = buildIntent()
    results.value = await structuredSearch({ ...intent, product_ids: scopeIds() ?? null })
    unresolved.value = results.value.needs_clarification ?? []
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : String(cause)
  } finally {
    searching.value = false
  }
}

async function runAssistant() {
  if (!question.value.trim() || answering.value) return
  answering.value = true
  error.value = null
  try {
    const response = await assistantQuery(question.value.trim(), scopeIds())
    answer.value = response
    results.value = response.search ?? null
    unresolved.value = response.search?.needs_clarification ?? []
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : String(cause)
  } finally {
    answering.value = false
  }
}

function expansion(productId: number): CardExpansion {
  return (expansions[productId] ??= {})
}

function reviewHeaderOf(productId: number) {
  const data = expansion(productId).reviews?.data
  return { unique: data?.unique_reviews ?? 0, analyzed: data?.gemini_reviews ?? null }
}

function reviewSummaryOf(productId: number): SummaryModel {
  const data = expansion(productId).reviews?.data
  return data ? buildSummaryModel(data) : { cards: [], showsDifferingExperiences: false, oneSidedSample: false }
}

function evidenceDataOf(productId: number) {
  return expansion(productId).evidence?.data ?? null
}

function alternativesOf(productId: number) {
  return expansion(productId).alternatives?.data?.alternatives ?? []
}

async function toggleEvidence(product: SearchProduct) {
  const state = expansion(product.id)
  if (state.evidence?.data) {
    state.evidence = undefined
    return
  }
  state.evidence = { loading: true }
  try {
    state.evidence = { loading: false, data: await fetchEvidence(product.evidence_id) }
  } catch (cause) {
    state.evidence = { loading: false, error: cause instanceof Error ? cause.message : String(cause) }
  }
}

async function toggleReviews(product: SearchProduct) {
  const state = expansion(product.id)
  if (state.reviews?.data) {
    state.reviews = undefined
    return
  }
  state.reviews = { loading: true }
  try {
    state.reviews = { loading: false, data: await fetchReviewInsights(product.id) }
  } catch (cause) {
    state.reviews = { loading: false, error: cause instanceof Error ? cause.message : String(cause) }
  }
}

async function analyzeMoreReviews(product: SearchProduct) {
  const state = expansion(product.id)
  if (!state.reviews) return
  state.reviews.preparing = true
  try {
    await prepareReviews(product.id, 10)
    state.reviews = { loading: false, data: await fetchReviewInsights(product.id) }
  } catch (cause) {
    state.reviews = { loading: false, error: cause instanceof Error ? cause.message : String(cause), data: state.reviews.data }
  } finally {
    state.reviews.preparing = false
  }
}

async function toggleAlternatives(product: SearchProduct) {
  const state = expansion(product.id)
  if (state.alternatives?.data) {
    state.alternatives = undefined
    return
  }
  state.alternatives = { loading: true }
  try {
    const productIds = results.value?.products.map(p => p.id).slice(0, 10)
    state.alternatives = { loading: false, data: await fetchAlternatives(product.id, lastIntent.value ?? buildIntent(), productIds) }
  } catch (cause) {
    state.alternatives = { loading: false, error: cause instanceof Error ? cause.message : String(cause) }
  }
}

/* Quote explorer state per product (pagination + combined filters). */
const QUOTE_PAGE = 6
const quoteFilters = reactive<Record<number, { aspect: string; sentiment: string; shown: number }>>({})

function quoteState(productId: number) {
  return (quoteFilters[productId] ??= { aspect: '', sentiment: '', shown: QUOTE_PAGE })
}

function observationsOf(productId: number): ObservationLike[] {
  return (expansions[productId]?.reviews?.data?.observations ?? []) as ObservationLike[]
}

function resetQuoteFilters(productId: number) {
  quoteFilters[productId] = { aspect: '', sentiment: '', shown: QUOTE_PAGE }
}

const EXAMPLES = [
  'Find moisturizers with ceramides. Summarize texture evidence and suggest one alternative.',
  'How do ceramide moisturizers feel?',
  'What do hydration reviews reveal?',
]
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="border-b pb-4">
      <span class="text-[11px] font-bold uppercase tracking-wider text-primary">Ask a question</span>
      <h2 class="text-2xl sm:text-3xl font-black tracking-tight mt-1">Go beyond the ingredient list.</h2>
      <p class="text-sm text-muted-foreground mt-1 max-w-2xl">
        Describe the ingredients or review themes you care about. Skintellect shows matching records, supporting quotes,
        and what remains unknown.
      </p>
    </div>

    <!-- Question panel -->
    <Card>
      <CardContent class="p-5 flex flex-col gap-3">
        <textarea
          v-model="question"
          rows="3"
          placeholder="e.g. Find moisturizers with ceramides. Summarize texture evidence and suggest one alternative."
          class="w-full rounded-xl border border-input bg-background p-3 text-sm leading-relaxed focus:outline-none focus:ring-1 focus:ring-primary"
        />
        <div class="flex flex-wrap items-center gap-1.5">
          <button
            v-for="example in EXAMPLES"
            :key="example"
            type="button"
            class="text-xs px-3 py-1 rounded-full border bg-background hover:bg-muted text-foreground transition-colors cursor-pointer"
            @click="question = example"
          >
            {{ example }}
          </button>
        </div>

        <div class="flex flex-wrap items-center gap-2 pt-1">
          <Button size="sm" class="gap-1.5 font-bold" :disabled="answering || !question.trim()" @click="runAssistant">
            <Loader2 v-if="answering" class="w-4 h-4 animate-spin" />
            <Search v-else class="w-4 h-4" />
            Find products & explain
          </Button>
          <label class="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer select-none">
            <input v-model="demoScope" type="checkbox" class="w-4 h-4 rounded cursor-pointer" />
            Search the prepared group only
          </label>
          <span v-if="demoScope" class="text-[11px] text-muted-foreground">{{ DEMO_HINT }}</span>
        </div>

        <p v-if="error" class="text-xs text-evidence-negative font-semibold flex items-center gap-1.5" role="alert">
          <AlertTriangle class="w-3.5 h-3.5" />
          {{ error }}
        </p>

        <!-- Editable filters filled from the question -->
        <div v-if="filtersVisible" class="border-t pt-3 flex flex-col gap-2.5">
          <button
            type="button"
            class="text-xs font-bold text-primary hover:underline flex items-center gap-1 cursor-pointer w-fit"
            @click="filtersVisible = !filtersVisible"
          >
            <ChevronDown class="w-3.5 h-3.5 transition-transform" :class="{ 'rotate-180': filtersVisible }" />
            Edit ingredient and category filters
          </button>
          <div v-if="filtersVisible" class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <label class="text-xs flex flex-col gap-1">
              <span class="font-semibold text-muted-foreground">Category</span>
              <select v-model="filters.category" class="h-9 rounded-lg border border-input bg-background px-2 text-xs cursor-pointer">
                <option value="all">All categories</option>
                <option value="Moisturizers">Moisturizers</option>
                <option value="Serums">Serums</option>
                <option value="Toners">Toners</option>
                <option value="Cleansers">Cleansers</option>
                <option value="Sunscreens">Sunscreens</option>
                <option value="Shampoos">Shampoos</option>
                <option value="Conditioners">Conditioners</option>
              </select>
            </label>
            <label class="text-xs flex flex-col gap-1">
              <span class="font-semibold text-muted-foreground">Domain</span>
              <select v-model="filters.domain" class="h-9 rounded-lg border border-input bg-background px-2 text-xs cursor-pointer">
                <option value="skin">Skin</option>
                <option value="hair">Hair</option>
                <option value="body">Body</option>
                <option value="makeup">Makeup</option>
                <option value="all">All</option>
              </select>
            </label>
            <label class="text-xs flex flex-col gap-1">
              <span class="font-semibold text-muted-foreground">Required ingredients (comma-separated)</span>
              <input v-model="filters.required_ingredients" class="h-9 rounded-lg border border-input bg-background px-2 text-xs" placeholder="ceramide, glycerin" />
            </label>
            <label class="text-xs flex flex-col gap-1">
              <span class="font-semibold text-muted-foreground">Excluded ingredients</span>
              <input v-model="filters.excluded_ingredients" class="h-9 rounded-lg border border-input bg-background px-2 text-xs" placeholder="fragrance, denatured alcohol" />
            </label>
            <label class="text-xs flex flex-col gap-1">
              <span class="font-semibold text-muted-foreground">Preferred price tier</span>
              <select v-model="filters.price" class="h-9 rounded-lg border border-input bg-background px-2 text-xs cursor-pointer">
                <option value="">Any price</option>
                <option value="$">$</option>
                <option value="$$">$$</option>
                <option value="$$$">$$$</option>
                <option value="$$$$">$$$$</option>
              </select>
            </label>
            <div class="flex items-end">
              <Button variant="outline" size="sm" class="gap-1.5" :disabled="searching" @click="runSearch">
                <Loader2 v-if="searching" class="w-3.5 h-3.5 animate-spin" />
                <Search v-else class="w-3.5 h-3.5" />
                Search using these filters
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Unresolved terms clarification -->
    <div
      v-if="unresolved.length > 0"
      class="p-3.5 rounded-xl border border-evidence-unknown/30 bg-evidence-unknown-bg/50 text-xs"
      role="status"
    >
      <span class="font-bold text-evidence-unknown">Unresolved terms:</span>
      {{ unresolved.join(', ') }} —
      refine the filters above so the search can apply verified constraints.
    </div>

    <!-- Assistant answer -->
    <Card v-if="answer">
      <CardHeader class="pb-3 border-b">
        <CardTitle class="text-base font-bold flex items-center gap-2">
          <MessageSquare class="w-4 h-4 text-primary" />
          Answer
        </CardTitle>
      </CardHeader>
      <CardContent class="p-5 text-xs flex flex-col gap-4">
        <p class="text-sm leading-relaxed text-foreground whitespace-pre-line">{{ answer.answer }}</p>

        <!-- Synthesis observations -->
        <div v-if="answer.synthesis?.selections?.length" class="flex flex-col gap-2">
          <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">Supporting quotes</span>
          <div
            v-for="(sel, idx) in answer.synthesis.selections.slice(0, 6)"
            :key="idx"
            class="p-2.5 rounded-xl border bg-background/80 flex flex-col gap-1"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="font-bold text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-muted text-foreground">
                {{ sel.aspect || sel.topic }}
              </span>
              <Badge v-if="sel.kind === 'reported_experience'" variant="source" class="text-[9px] py-0">Reviewer experience</Badge>
            </div>
            <p class="italic text-foreground/90 font-serif text-[11px]">"{{ sel.span || sel.quote }}"</p>
          </div>
        </div>
        <p v-if="answer.synthesis?.unanswered_topics?.length" class="text-[11px] text-muted-foreground">
          <span class="font-bold text-evidence-unknown">Not answered by the collected evidence:</span>
          {{ answer.synthesis.unanswered_topics.join(', ') }}
        </p>

        <!-- References -->
        <div v-if="answer.references?.length" class="flex flex-col gap-1.5">
          <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">References</span>
          <div v-for="ref in answer.references.slice(0, 4)" :key="ref.evidence_id ?? ref.title" class="text-[11px] text-muted-foreground">
            <span class="font-bold text-foreground">{{ ref.title }}</span>
            <template v-if="ref.summary"> — {{ ref.summary.slice(0, 180) }}</template>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Results -->
    <div v-if="results" class="flex flex-col gap-3">
      <div class="flex items-baseline justify-between flex-wrap gap-2">
        <h3 class="text-base font-bold">Matching records</h3>
        <span class="text-xs text-muted-foreground">
          {{ results.total }} match<template v-if="results.total !== 1">es</template>
          <template v-if="results.unknown_count"> · {{ results.unknown_count }} with unknown ingredients</template>
          <template v-if="results.failed_count"> · {{ results.failed_count }} unusable</template>
        </span>
      </div>
      <p v-if="results.notice" class="text-[11px] text-muted-foreground">{{ results.notice }}</p>

      <div v-if="results.products.length === 0" class="py-10 text-center border rounded-xl bg-card text-sm text-muted-foreground">
        No records match these constraints. Try relaxing an exclusion or widening the category.
      </div>

      <Card v-for="p in results.products" :key="p.id" class="overflow-hidden">
        <CardHeader class="pb-2">
          <div class="flex items-start justify-between gap-2 flex-wrap">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{{ p.brand }}</span>
              <CardTitle class="text-sm font-bold">{{ p.name }}</CardTitle>
            </div>
            <div class="flex items-center gap-1.5">
              <Badge variant="outline" class="text-[10px]">{{ p.price_tier || '$$' }}</Badge>
              <Badge v-if="p.formula_status === 'verified_complete'" variant="verified" class="text-[10px]">Verified INCI</Badge>
              <Badge v-else variant="unknown" class="text-[10px]">Unverified list</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent class="pt-0 pb-4 flex flex-col gap-3 text-xs">
          <!-- Constraint checks -->
          <div v-if="p.checks?.length" class="flex flex-col gap-1">
            <div v-for="(check, idx) in p.checks" :key="idx" class="flex items-center gap-1.5 text-[11px]">
              <span
                class="w-1.5 h-1.5 rounded-full shrink-0"
                :class="check.status === 'pass' ? 'bg-emerald-500' : check.status === 'fail' ? 'bg-rose-500' : 'bg-amber-400'"
              />
              <span class="text-muted-foreground">{{ check.constraint }}</span>
              <span v-if="check.matched_names?.length" class="text-foreground font-semibold">{{ check.matched_names.join(', ') }}</span>
            </div>
          </div>

          <!-- Expanders -->
          <div class="flex items-center gap-2 flex-wrap">
            <Button variant="outline" size="sm" class="h-7 text-[11px] gap-1" @click="toggleEvidence(p)">
              <BookOpen class="w-3 h-3" /> Evidence
            </Button>
            <Button variant="outline" size="sm" class="h-7 text-[11px] gap-1" @click="toggleReviews(p)">
              <MessageSquare class="w-3 h-3" /> Reviews
            </Button>
            <Button variant="outline" size="sm" class="h-7 text-[11px] gap-1" @click="toggleAlternatives(p)">
              <Scale class="w-3 h-3" /> Alternatives
            </Button>
          </div>

          <!-- Evidence drawer -->
          <div v-if="expansion(p.id).evidence" class="p-3 rounded-xl border bg-muted/20 text-[11px] flex flex-col gap-1.5">
            <Loader2 v-if="expansion(p.id).evidence!.loading" class="w-4 h-4 animate-spin text-primary" />
            <template v-else-if="expansion(p.id).evidence!.error">
              <span class="text-evidence-negative font-semibold">{{ expansion(p.id).evidence!.error }}</span>
            </template>
            <template v-else-if="evidenceDataOf(p.id)">
              <template v-if="evidenceDataOf(p.id)?.kind === 'catalog_record'">
                <span class="font-bold text-foreground">Recorded description</span>
                <p class="text-muted-foreground">{{ evidenceDataOf(p.id)?.description || 'Not recorded.' }}</p>
              </template>
              <template v-else-if="evidenceDataOf(p.id)?.kind === 'reported_experience'">
                <p class="italic font-serif text-foreground/90">"{{ evidenceDataOf(p.id)?.cleaned_text || evidenceDataOf(p.id)?.review_text }}"</p>
                <span class="text-muted-foreground">Recorded {{ evidenceDataOf(p.id)?.date_posted || 'date unknown' }}</span>
              </template>
              <template v-else>
                <pre class="font-mono text-[10px] whitespace-pre-wrap max-h-40 overflow-y-auto">{{ JSON.stringify(evidenceDataOf(p.id), null, 2) }}</pre>
              </template>
            </template>
          </div>

          <!-- Reviews drawer with quote explorer -->
          <div v-if="expansion(p.id).reviews" class="p-3 rounded-xl border bg-muted/20 text-[11px] flex flex-col gap-2.5">
            <Loader2 v-if="expansion(p.id).reviews!.loading" class="w-4 h-4 animate-spin text-primary" />
            <template v-else-if="expansion(p.id).reviews!.error">
              <span class="text-evidence-negative font-semibold">{{ expansion(p.id).reviews!.error }}</span>
            </template>
            <template v-else-if="expansion(p.id).reviews?.data">
              <div class="flex items-center justify-between flex-wrap gap-2">
                <span class="font-bold text-foreground">
                  {{ reviewHeaderOf(p.id).unique }} unique reviews
                  <template v-if="reviewHeaderOf(p.id).analyzed !== null">
                    · {{ reviewHeaderOf(p.id).analyzed }} analyzed
                  </template>
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  class="h-6 text-[10px]"
                  :disabled="expansion(p.id).reviews!.preparing"
                  @click="analyzeMoreReviews(p)"
                >
                  <Loader2 v-if="expansion(p.id).reviews!.preparing" class="w-3 h-3 animate-spin" />
                  Analyze up to 10 more reviews
                </Button>
              </div>

              <!-- Summary cards from shared evidence semantics -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <div
                  v-for="card in reviewSummaryOf(p.id).cards.slice(0, 4)"
                  :key="card.aspect"
                  class="p-2 rounded-lg border bg-card"
                >
                  <div class="font-bold text-foreground">{{ card.label }}</div>
                  <div class="text-muted-foreground">{{ card.mentioning }} of {{ card.denominator }}</div>
                  <div class="flex items-center gap-1 mt-0.5 text-[10px]">
                    <span v-if="card.positive" class="text-emerald-700">+{{ card.positive }}</span>
                    <span v-if="card.negative" class="text-rose-700">−{{ card.negative }}</span>
                    <span v-if="card.mixed" class="text-purple-700">±{{ card.mixed }}</span>
                  </div>
                </div>
              </div>
              <p v-if="reviewSummaryOf(p.id).oneSidedSample" class="text-[10px] text-muted-foreground italic">
                A one-sided extracted sample does not establish that reviewers agree.
              </p>

              <!-- Quote explorer -->
              <div class="border-t pt-2 flex flex-col gap-2">
                <div class="flex items-center gap-2 flex-wrap">
                  <select
                    v-model="quoteState(p.id).aspect"
                    class="h-7 rounded-lg border border-input bg-background px-2 text-[11px] cursor-pointer"
                    @change="quoteState(p.id).shown = QUOTE_PAGE"
                  >
                    <option value="">All themes</option>
                    <option v-for="aspect in [...new Set(observationsOf(p.id).map(o => aspectLabel(o.aspect || o.topic || 'unspecified')))]" :key="aspect" :value="aspect">
                      {{ aspect }}
                    </option>
                  </select>
                  <select
                    v-model="quoteState(p.id).sentiment"
                    class="h-7 rounded-lg border border-input bg-background px-2 text-[11px] cursor-pointer"
                    @change="quoteState(p.id).shown = QUOTE_PAGE"
                  >
                    <option value="">All experiences</option>
                    <option value="positive">Positive</option>
                    <option value="negative">Negative</option>
                    <option value="mixed">Mixed</option>
                    <option value="neutral">Neutral</option>
                    <option value="unspecified">Unlabeled</option>
                  </select>
                  <button
                    type="button"
                    class="text-[10px] font-semibold text-muted-foreground hover:text-foreground cursor-pointer"
                    :disabled="!quoteState(p.id).aspect && !quoteState(p.id).sentiment"
                    @click="resetQuoteFilters(p.id)"
                  >
                    Clear filters
                  </button>
                </div>

                <div
                  v-for="obs in filterObservations(observationsOf(p.id), quoteState(p.id).aspect, quoteState(p.id).sentiment).slice(0, quoteState(p.id).shown)"
                  :key="(obs.evidence_id ?? obs.span) as string"
                  class="p-2 rounded-lg border bg-background/80"
                >
                  <div class="flex items-center justify-between gap-2 text-[10px]">
                    <span class="font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-muted text-foreground">{{ obs.aspect || obs.topic }}</span>
                    <span
                      class="font-bold px-1.5 py-0.5 rounded"
                      :class="obs.sentiment === 'negative' ? 'bg-rose-100 text-rose-800' : obs.sentiment === 'positive' ? 'bg-emerald-100 text-emerald-800' : obs.sentiment === 'mixed' ? 'bg-purple-100 text-purple-800' : 'bg-muted text-muted-foreground'"
                    >
                      {{ obs.sentiment || 'observed' }}
                    </span>
                  </div>
                  <p class="italic font-serif text-foreground/90 mt-1">"{{ obs.span || obs.quote }}"</p>
                </div>

                <p
                  v-if="filterObservations(observationsOf(p.id), quoteState(p.id).aspect, quoteState(p.id).sentiment).length === 0"
                  class="text-muted-foreground italic"
                >
                  No observations match both filters.
                </p>
                <button
                  v-else-if="quoteState(p.id).shown < filterObservations(observationsOf(p.id), quoteState(p.id).aspect, quoteState(p.id).sentiment).length"
                  type="button"
                  class="text-[10px] font-bold text-primary hover:underline w-fit cursor-pointer"
                  @click="quoteState(p.id).shown += QUOTE_PAGE"
                >
                  Show more quotes
                </button>
              </div>
            </template>
          </div>

          <!-- Alternatives drawer -->
          <div v-if="expansion(p.id).alternatives" class="p-3 rounded-xl border bg-muted/20 text-[11px] flex flex-col gap-2">
            <Loader2 v-if="expansion(p.id).alternatives?.loading" class="w-4 h-4 animate-spin text-primary" />
            <template v-else-if="expansion(p.id).alternatives?.error">
              <span class="text-evidence-negative font-semibold">{{ expansion(p.id).alternatives?.error }}</span>
            </template>
            <template v-else-if="expansion(p.id).alternatives?.data">
              <div v-if="alternativesOf(p.id).length === 0" class="text-muted-foreground italic">
                No formula alternatives matched these constraints.
              </div>
              <div
                v-for="alt in alternativesOf(p.id).slice(0, 3)"
                :key="alt.evidence_id ?? alt.name"
                class="p-2 rounded-lg border bg-background/80"
              >
                <div class="flex items-center justify-between gap-2 font-bold text-foreground">
                  <span>{{ alt.brand }} — {{ alt.name }}</span>
                  <span class="font-mono text-primary">{{ alt.weighted_similarity ? Math.round(alt.weighted_similarity * 100) + '%' : '' }}</span>
                </div>
                <p class="text-muted-foreground mt-0.5">
                  Shared: {{ (alt.shared_ingredients ?? []).slice(0, 5).join(', ') || '—' }}
                </p>
              </div>
            </template>
          </div>
        </CardContent>
      </Card>
    </div>

    <p v-else-if="notice" class="text-[11px] text-muted-foreground">{{ notice }}</p>
  </div>
</template>
