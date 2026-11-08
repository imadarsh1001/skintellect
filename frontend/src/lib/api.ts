import type { Product, SkinPersona, IngredientGraphData } from './types'

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

export async function fetchProducts(filters: ProductFilters = {}): Promise<ProductsResponse> {
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

  const res = await fetch(`${BASE_URL}/api/products?${params.toString()}`)
  if (!res.ok) throw new Error(`Failed to fetch products: ${res.statusText}`)
  return res.json()
}

export async function fetchProduct(id: number, personaId = 'uap'): Promise<Product> {
  const res = await fetch(`${BASE_URL}/api/products/${id}?persona_id=${encodeURIComponent(personaId)}`)
  if (!res.ok) throw new Error(`Failed to fetch product ${id}`)
  return res.json()
}

export async function fetchPersonas(): Promise<SkinPersona[]> {
  const res = await fetch(`${BASE_URL}/api/personas`)
  if (!res.ok) throw new Error('Failed to fetch personas')
  return res.json()
}

export async function savePersona(persona: Partial<SkinPersona>): Promise<SkinPersona> {
  const res = await fetch(`${BASE_URL}/api/personas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(persona),
  })
  if (!res.ok) throw new Error('Failed to save persona')
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

export async function fetchReviewInsights(productId: number): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/products/${productId}/review-insights`)
  if (!res.ok) throw new Error(`Failed to fetch reviews for product ${productId}`)
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
    const fallback = await askCopilot(payload)
    onUpdate({ event: 'final_result', data: fallback })
    return fallback
  } catch (err) {
    console.warn('Stream failed, falling back to standard copilot ask:', err)
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

