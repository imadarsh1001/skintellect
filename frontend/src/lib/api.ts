import type { CatalogStats, Product, ProductConnections, SkinPersona } from './types'

export type { CatalogStats, ProductConnections } from './types'

const BASE_URL = ''

export interface ProductFilters {
  page?: number
  limit?: number
  category?: string
  domain?: string
  price_tier?: string
  country?: string
  goal?: string
  min_match?: number
  search?: string
  fungal_safe?: boolean
  fragrance_free?: boolean
  oil_free?: boolean
  pore_free?: boolean
  sort_by?: string
  persona_id?: string
  include_seeds?: boolean
}

export interface ProductsResponse {
  total: number
  page: number
  limit: number
  products: Product[]
}

export async function fetchProducts(filters: ProductFilters = {}, signal?: AbortSignal): Promise<ProductsResponse> {
  const params = new URLSearchParams()
  if (filters.page) params.set('page', filters.page.toString())
  if (filters.limit) params.set('limit', filters.limit.toString())
  if (filters.category) params.set('category', filters.category)
  if (filters.domain) params.set('domain', filters.domain)
  if (filters.price_tier) params.set('price_tier', filters.price_tier)
  if (filters.country) params.set('country', filters.country)
  if (filters.goal) params.set('goal', filters.goal)
  if (filters.min_match !== undefined) params.set('min_match', filters.min_match.toString())
  if (filters.search) params.set('search', filters.search)
  if (filters.fungal_safe) params.set('fungal_safe', 'true')
  if (filters.fragrance_free) params.set('fragrance_free', 'true')
  if (filters.oil_free) params.set('oil_free', 'true')
  if (filters.pore_free) params.set('pore_free', 'true')
  if (filters.sort_by) params.set('sort_by', filters.sort_by)
  if (filters.persona_id) params.set('persona_id', filters.persona_id)
  if (filters.include_seeds) params.set('include_seeds', 'true')

  const res = await fetch(`${BASE_URL}/api/products?${params.toString()}`, { signal })
  if (!res.ok) throw new Error(`Failed to fetch products: ${res.statusText}`)
  return res.json()
}

export async function fetchProduct(id: number, personaId = 'uap'): Promise<Product> {
  const res = await fetch(`${BASE_URL}/api/products/${id}?persona_id=${encodeURIComponent(personaId)}`)
  if (!res.ok) throw new Error(`Failed to fetch product ${id}`)
  return res.json()
}

/**
 * The backend PersonaModel speaks `label` / `target_concerns` /
 * `safety_exclusions`; the UI speaks `name` / `concerns` / `exclude_*`.
 * Adapter keeps the API contract authoritative and the UI model ergonomic.
 */
interface BackendPersona {
  id: string
  username: string
  label: string
  description?: string
  skin_type: SkinPersona['skin_type']
  sensitivity?: string
  target_concerns?: string[]
  safety_exclusions?: {
    fungal_acne_safe?: boolean
    fragrance_free?: boolean
    alcohol_free?: boolean
    oil_free?: boolean
    pore_clogger_free?: boolean
  }
  is_default?: number
}

function adaptPersona(raw: BackendPersona): SkinPersona {
  return {
    id: raw.id,
    username: raw.username,
    name: raw.label || raw.id,
    skin_type: raw.skin_type,
    concerns: raw.target_concerns ?? [],
    goals: [],
    exclude_fungal_acne_triggers: raw.safety_exclusions?.fungal_acne_safe ?? false,
    exclude_drying_alcohols: raw.safety_exclusions?.alcohol_free ?? false,
    exclude_fragrance: raw.safety_exclusions?.fragrance_free ?? false,
    custom_exclusions: [],
    sensitivity: raw.sensitivity,
    description: raw.description,
    is_default: raw.is_default,
  }
}

export async function fetchPersonas(): Promise<SkinPersona[]> {
  const res = await fetch(`${BASE_URL}/api/personas`)
  if (!res.ok) throw new Error('Failed to fetch personas')
  const raw: BackendPersona[] = await res.json()
  return raw.map(adaptPersona)
}

export async function savePersona(persona: Partial<SkinPersona>): Promise<SkinPersona> {
  const username = persona.username || persona.id || `custom_${Date.now()}`
  const body = {
    username,
    label: persona.name || username,
    description: persona.description ?? '',
    skin_type: persona.skin_type ?? 'combination',
    sensitivity: persona.sensitivity ?? 'slightly_sensitive',
    target_concerns: persona.concerns ?? [],
    safety_exclusions: {
      fungal_acne_safe: persona.exclude_fungal_acne_triggers ?? false,
      fragrance_free: persona.exclude_fragrance ?? false,
      alcohol_free: persona.exclude_drying_alcohols ?? false,
      oil_free: false,
      pore_clogger_free: true,
    },
  }
  const res = await fetch(`${BASE_URL}/api/personas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`Failed to save persona: ${res.status}`)
  return adaptPersona(await res.json())
}

export async function fetchCatalogStats(): Promise<CatalogStats> {
  const res = await fetch(`${BASE_URL}/api/stats`)
  if (!res.ok) throw new Error('Failed to fetch catalog stats')
  return res.json()
}

export async function fetchConnections(productId: number, limit = 5): Promise<ProductConnections> {
  const res = await fetch(`${BASE_URL}/api/products/${productId}/connections?limit=${limit}`)
  if (!res.ok) throw new Error(`Failed to fetch connections for product ${productId}`)
  return res.json()
}

export async function fetchDupes(productId: number): Promise<{ product_id: number; dupes: any[] }> {
  const res = await fetch(`${BASE_URL}/api/dupes/${productId}`)
  if (!res.ok) throw new Error(`Failed to fetch dupes for product ${productId}`)
  return res.json()
}

export async function fetchEvidence(evidenceId: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/evidence/${encodeURIComponent(evidenceId)}`)
  if (!res.ok) throw new Error(`Failed to fetch evidence ${evidenceId}`)
  return res.json()
}

export async function askCopilot(payload: {
  session_id?: string
  persona_id?: string
  query: string
  product_ids?: number[]
  planning_mode?: string
}): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/research/copilot`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(`Copilot request failed: ${res.statusText}`)
  return res.json()
}

export async function streamCopilot(
  payload: {
    session_id?: string
    persona_id?: string
    query: string
    product_ids?: number[]
    planning_mode?: string
  },
  onUpdate: (event: { event: string; node?: string; data: any }) => void
): Promise<any> {
  try {
    const res = await fetch(`${BASE_URL}/api/research/copilot/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok || !res.body) {
      // Degraded mode must be observable, never silent (redesign D1).
      console.warn('[copilot] SSE stream unavailable; falling back to non-streaming query')
      onUpdate({ event: 'stream_fallback', data: { reason: 'stream_unavailable' } })
      const fallback = await askCopilot(payload)
      onUpdate({ event: 'final_result', data: fallback })
      return fallback
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let finalData: any = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const chunk of lines) {
        const trimmed = chunk.trim()
        if (!trimmed || !trimmed.startsWith('data: ')) continue
        const rawData = trimmed.slice(6).trim()
        if (rawData === '[DONE]') continue
        try {
          const parsed = JSON.parse(rawData)
          onUpdate(parsed)
          if (parsed.event === 'final_result') {
            finalData = parsed.data
          }
        } catch (e) {
          console.warn('Failed to parse SSE event chunk:', rawData, e)
        }
      }
    }

    if (finalData) return finalData
    console.warn('[copilot] SSE stream ended without a final result; falling back to non-streaming query')
    onUpdate({ event: 'stream_fallback', data: { reason: 'no_final_result' } })
    const fallback = await askCopilot(payload)
    onUpdate({ event: 'final_result', data: fallback })
    return fallback
  } catch (err) {
    console.warn('[copilot] Stream failed, falling back to non-streaming query:', err)
    onUpdate({ event: 'stream_fallback', data: { reason: 'stream_error' } })
    const fallback = await askCopilot(payload)
    onUpdate({ event: 'final_result', data: fallback })
    return fallback
  }
}

export async function fetchCopilotSessions(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/api/research/copilot/sessions`)
  if (!res.ok) throw new Error('Failed to fetch copilot sessions')
  return res.json()
}

export async function createCopilotSession(personaId = 'uap'): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/research/copilot/sessions/new?persona_id=${encodeURIComponent(personaId)}`, {
    method: 'POST',
  })
  if (!res.ok) throw new Error('Failed to create new copilot session')
  return res.json()
}

export async function deleteCopilotSession(sessionId: string): Promise<boolean> {
  const res = await fetch(`${BASE_URL}/api/research/copilot/sessions/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  })
  return res.ok
}

export async function fetchCopilotSession(sessionId: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/research/copilot/sessions/${encodeURIComponent(sessionId)}`)
  if (!res.ok) throw new Error(`Failed to fetch session ${sessionId}`)
  return res.json()
}

/* ---------------------------------------------------------------------------
 * Evidence-research endpoints (Stage 5: SPA replacements for the legacy
 * /research, /study and /progress pages). Field names mirror the backend
 * models in skintellect/research/models.py exactly — StrictModel rejects
 * unknown fields, so these bodies must stay minimal.
 * ------------------------------------------------------------------------- */

export interface SearchIntentPayload {
  category?: string
  domain?: 'skin' | 'hair' | 'body' | 'makeup' | 'all'
  required_ingredients?: string[]
  excluded_ingredients?: string[]
  preferred_price_tiers?: string[]
  preferences?: string[]
  unresolved_terms?: string[]
  text?: string
  limit?: number
  product_ids?: number[] | null
}

export interface SearchCheck {
  constraint: string
  status: 'pass' | 'fail' | 'unknown'
  matched_names?: string[]
  reason?: string
  evidence_ids?: string[]
}

export interface SearchProduct {
  id: number
  brand: string
  name: string
  category?: string
  price_tier?: string
  url?: string
  formula_status?: string
  evidence_id: string
  checks?: SearchCheck[]
  ranking_components?: Record<string, number>
}

export interface StructuredSearchResponse {
  products: SearchProduct[]
  total: number
  unknown_count: number
  failed_count: number
  needs_clarification: string[]
  notice?: string
}

export async function searchInterpret(query: string): Promise<{ intent: SearchIntentPayload; mode?: string; notice?: string }> {
  const res = await fetch(`${BASE_URL}/api/search/interpret`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!res.ok) throw new Error(`Failed to interpret the question: ${res.status}`)
  return res.json()
}

export async function structuredSearch(intent: SearchIntentPayload): Promise<StructuredSearchResponse> {
  const res = await fetch(`${BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(intent),
  })
  if (!res.ok) throw new Error(`Search failed: ${res.status}`)
  return res.json()
}

export interface AssistantResponse {
  answer?: string
  search?: StructuredSearchResponse
  review_insights?: ReviewInsights[]
  alternatives?: AlternativesResponse[]
  references?: ReferenceRecord[]
  synthesis?: {
    mode?: string
    selections?: Array<{ evidence_id?: string; topic?: string; aspect?: string; sentiment?: string; span?: string; quote?: string; kind?: string }>
    unanswered_topics?: string[]
    error_code?: string
  }
  trace?: Record<string, unknown>
}

export async function assistantQuery(query: string, productIds?: number[]): Promise<AssistantResponse> {
  const res = await fetch(`${BASE_URL}/api/assistant/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productIds && productIds.length > 0 ? { query, product_ids: productIds } : { query }),
  })
  if (!res.ok) throw new Error(`The assistant request failed: ${res.status}`)
  return res.json()
}

export interface DemoProduct {
  id: number
  brand: string
  name: string
  recorded_ingredients?: number
  selected_reviews?: number
  available?: boolean
  reviews: { eligible: number; processed: number }
  passages: { eligible: number; indexed: number }
  ready: boolean
}

export interface EvaluationReport {
  review_agreement?: { reviews?: number; invalid_model_source_spans?: number; exact_set_agreement?: number | null }
  latency?: { measurements?: Array<{ elapsed_ms?: number }>; limitation?: string }
  retrieval?: {
    cases?: unknown[]
    summary?: Record<string, { mrr?: number; recall_at_3?: number }>
  }
  [key: string]: unknown
}

export interface DemoReadiness {
  configured: boolean
  ready: boolean
  products: DemoProduct[]
  product_ids?: number[]
  example_query?: string
  evaluation?: EvaluationReport | null
  evaluation_current?: boolean
}

export async function fetchDemo(): Promise<DemoReadiness> {
  const res = await fetch(`${BASE_URL}/api/research/demo`)
  if (!res.ok) throw new Error('Failed to fetch the prepared study status')
  return res.json()
}

export interface ReferenceRecord {
  id?: string
  title: string
  publisher?: string
  url?: string
  source_type?: string
  topics?: string[]
  quote?: string
  summary?: string
  limitations?: string
  retrieved_at?: string
  evidence_id?: string
}

export async function fetchReferences(q?: string): Promise<{ references: ReferenceRecord[]; notice: string }> {
  const params = q ? `?q=${encodeURIComponent(q)}` : ''
  const res = await fetch(`${BASE_URL}/api/research/references${params}`)
  if (!res.ok) throw new Error('Failed to fetch reference notes')
  return res.json()
}

export interface QualityAudit {
  products?: number
  ingredients?: number
  reviews?: number
  source_documents?: number
  seed_products?: number
  formulas_present?: number
  verified_complete?: number
  truncated_reviews?: number
  [key: string]: unknown
}

export async function fetchQuality(): Promise<QualityAudit> {
  const res = await fetch(`${BASE_URL}/api/quality`)
  if (!res.ok) throw new Error('Failed to fetch quality checks')
  return res.json()
}

export interface PreparationJobRow {
  id: number
  kind: string
  status: string
  cancel_requested?: number
  completed?: number
  selected?: number
  product_id?: number | null
  error_code?: string | null
  created_at?: string
  calls?: number
  max_calls?: number
  tokens?: number
  limit_count?: number
}

export interface ProgressSnapshot {
  model?: { enabled?: boolean; model?: string; [key: string]: unknown }
  reviews: { processed: number; eligible: number }
  embeddings: { indexed: number; eligible: number; remaining?: number; stale_or_out_of_scope?: number }
  usage?: { operations?: number; provider_attempts?: number; reported_tokens?: number; cache_hits?: number }
  jobs?: PreparationJobRow[]
  recent_operations?: Array<{ task?: string; status?: string; attempts?: number; elapsed_ms?: number; error_code?: string | null; created_at?: string }>
  notice?: string
}

export async function fetchProgress(): Promise<ProgressSnapshot> {
  const res = await fetch(`${BASE_URL}/api/research/progress`)
  if (!res.ok) throw new Error('Failed to fetch preparation progress')
  return res.json()
}

export async function submitPreparationJob(body: {
  kind: 'reviews' | 'embed'
  limit: number
  product_id: number | null
  max_calls: number
  max_seconds: number
}): Promise<{ job_id: number; status: string }> {
  const res = await fetch(`${BASE_URL}/api/research/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`The preparation job was rejected: ${res.status}`)
  return res.json()
}

export async function cancelPreparationJob(jobId: number): Promise<{ status: string; notice: string }> {
  const res = await fetch(`${BASE_URL}/api/research/jobs/${jobId}/cancel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  })
  if (!res.ok) throw new Error('Could not request cancellation for an active job')
  return res.json()
}

export interface ReviewInsights {
  product_id?: number
  collected_reviews?: number
  unique_reviews: number
  duplicates_removed?: number
  aspects: Array<{ aspect: string; is_discovered_aspect?: boolean; mentioning_reviews: number; positive_reviews: number; negative_reviews: number; mixed_reviews: number; neutral_reviews: number }>
  observations: ReviewObservation[]
  extraction_version?: string
  mode?: string
  gemini_reviews?: number
  notice?: string
}

export interface ReviewObservation {
  aspect?: string
  topic?: string
  is_discovered_aspect?: boolean
  sentiment?: 'positive' | 'negative' | 'neutral' | 'mixed'
  negated?: boolean
  span?: string
  quote?: string
  start?: number
  end?: number
  review_id?: number
  evidence_id?: string
  skin_type?: string
  truncated?: boolean
}

export async function fetchReviewInsights(productId: number): Promise<ReviewInsights> {
  const res = await fetch(`${BASE_URL}/api/products/${productId}/review-insights`)
  if (!res.ok) throw new Error(`Failed to fetch review insights for product ${productId}`)
  return res.json()
}

export async function prepareReviews(productId: number, limit = 10): Promise<{ processed_reviews: number; selected_reviews: number }> {
  const res = await fetch(`${BASE_URL}/api/research/reviews/prepare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId, limit }),
  })
  if (!res.ok) throw new Error(`Review analysis could not run: ${res.status}`)
  return res.json()
}

export interface AlternativesResponse {
  product_id: number
  alternatives: Array<{
    id?: number
    brand: string
    name: string
    price_tier?: string
    evidence_id?: string
    shared_ingredients?: string[]
    removed_ingredients?: string[]
    added_ingredients?: string[]
    weighted_similarity?: number
  }>
  needs_clarification?: string[]
  notice?: string
}

export async function fetchAlternatives(productId: number, constraints?: SearchIntentPayload, productIds?: number[]): Promise<AlternativesResponse> {
  const body: Record<string, unknown> = { product_id: productId }
  if (constraints) body.constraints = constraints
  if (productIds && productIds.length > 0) body.product_ids = productIds
  const res = await fetch(`${BASE_URL}/api/alternatives`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`Could not look up formula alternatives: ${res.status}`)
  return res.json()
}

