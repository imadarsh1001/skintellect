import { refDebounced } from '@vueuse/core'
import { computed, shallowRef, watch, type Ref } from 'vue'
import { useRoute, useRouter, type LocationQueryRaw } from 'vue-router'
import { fetchProducts } from '@/lib/api'
import type { Product } from '@/lib/types'

/**
 * URL-owned explore query state: the query string on the explore route is
 * the single source of truth for filters, sort, and page, so any view restores
 * exactly from a deep link. Product loading is debounced for the search input
 * and cancels in-flight requests when the query changes.
 */

export const DEFAULT_FILTERS = {
  search: '',
  domain: 'all',
  category: 'all',
  country: 'all',
  goal: 'all',
  price_tier: 'all',
  fungal_safe: false,
  fragrance_free: false,
  oil_free: false,
  pore_free: false,
  min_match: 0,
  sort_by: 'composite_desc',
  page: 1,
} as const

type FilterKey = keyof typeof DEFAULT_FILTERS
type FilterValues = { [K in FilterKey]: (typeof DEFAULT_FILTERS)[K] }

const BOOL_KEYS = new Set<FilterKey>(['fungal_safe', 'fragrance_free', 'oil_free', 'pore_free'])
const NUM_KEYS = new Set<FilterKey>(['min_match', 'page'])
// Not user "filters" in the count badge: sort strategy and pagination.
const UNCOUNTED_KEYS = new Set<FilterKey>(['sort_by', 'page'])

function readQuery(query: Record<string, unknown>): { filters: FilterValues; activeFilterCount: number } {
  const filters = { ...DEFAULT_FILTERS } as FilterValues
  let activeFilterCount = 0
  for (const key of Object.keys(DEFAULT_FILTERS) as FilterKey[]) {
    const raw = query[key]
    if (raw === undefined || raw === '' || raw === null) continue
    if (BOOL_KEYS.has(key)) {
      const value = raw === 'true' || raw === '1'
      filters[key] = value as never
      if (value && !UNCOUNTED_KEYS.has(key)) activeFilterCount++
    } else if (NUM_KEYS.has(key)) {
      const value = Number(raw)
      if (Number.isFinite(value)) {
        filters[key] = value as never
        if (key === 'min_match' && value > 0) activeFilterCount++
      }
    } else {
      const value = String(raw)
      if (value !== 'all' && !UNCOUNTED_KEYS.has(key)) activeFilterCount++
      filters[key] = value as never
    }
  }
  return { filters, activeFilterCount }
}

export function useExploreQuery(options: { personaId: Readonly<Ref<string>> }) {
  const route = useRoute()
  const router = useRouter()

  const products = shallowRef<Product[]>([])
  const total = shallowRef(0)
  const loading = shallowRef(false)
  const error = shallowRef<string | null>(null)
  const activeFilterCount = shallowRef(0)

  let inFlight: AbortController | null = null

  // Search input keeps local (per-keystroke) state; the debounced value drives the URL.
  const searchInput = shallowRef(String(route.query.search ?? ''))
  const searchDebounced = refDebounced(searchInput, 300)

  watch(searchDebounced, (value) => {
    if (String(route.query.search ?? '') === value) return
    setParams({ search: value || undefined, page: undefined })
  })

  // External query changes (reset, back/forward, deep link) sync the input back.
  watch(
    () => String(route.query.search ?? ''),
    (value) => {
      if (value !== searchInput.value) searchInput.value = value
    },
  )

  const filters = computed<FilterValues>(() => readQuery(route.query as Record<string, unknown>).filters)
  const page = computed(() => readQuery(route.query as Record<string, unknown>).filters.page)

  function setParams(patch: LocationQueryRaw) {
    const query: Record<string, LocationQueryRaw[string]> = { ...route.query, ...patch }
    for (const key of Object.keys(query)) {
      const value = query[key]
      if (value === undefined || value === null || value === '') delete query[key]
    }
    router.push({ query })
  }

  function setFilter(key: FilterKey, value: string | number | boolean) {
    const isDefault =
      value === DEFAULT_FILTERS[key] || value === 'all' || value === 0 || value === false
    if (isDefault) {
      setParams({ [key]: undefined, ...(key !== 'page' ? { page: undefined } : {}) })
      return
    }
    const serialized = typeof value === 'boolean' ? 'true' : value
    setParams({ [key]: serialized, ...(key !== 'page' ? { page: undefined } : {}) })
  }

  function setPage(value: number) {
    setParams({ page: value > 1 ? value : undefined })
  }

  function resetFilters() {
    searchInput.value = ''
    router.push({ query: {} })
  }

  async function load() {
    inFlight?.abort()
    const controller = new AbortController()
    inFlight = controller
    loading.value = true
    error.value = null
    const current = readQuery(route.query as Record<string, unknown>)
    activeFilterCount.value = current.activeFilterCount
    try {
      const response = await fetchProducts(
        {
          page: current.filters.page,
          search: current.filters.search || undefined,
          domain: current.filters.domain !== 'all' ? current.filters.domain : undefined,
          category: current.filters.category !== 'all' ? current.filters.category : undefined,
          country: current.filters.country !== 'all' ? current.filters.country : undefined,
          goal: current.filters.goal !== 'all' ? current.filters.goal : undefined,
          price_tier: current.filters.price_tier !== 'all' ? current.filters.price_tier : undefined,
          fungal_safe: current.filters.fungal_safe,
          fragrance_free: current.filters.fragrance_free,
          oil_free: current.filters.oil_free,
          pore_free: current.filters.pore_free,
          min_match: current.filters.min_match > 0 ? current.filters.min_match : undefined,
          sort_by: current.filters.sort_by,
          persona_id: options.personaId.value,
        },
        controller.signal,
      )
      if (controller !== inFlight) return
      products.value = response.products ?? []
      total.value = response.total ?? 0
    } catch (cause) {
      if (controller !== inFlight) return // superseded by a newer query
      if (cause instanceof DOMException && cause.name === 'AbortError') return
      error.value = cause instanceof Error ? cause.message : String(cause)
      products.value = []
      total.value = 0
    } finally {
      if (controller === inFlight) {
        inFlight = null
        loading.value = false
      }
    }
  }

  watch(
    () => [route.query, options.personaId.value] as const,
    () => {
      load()
    },
    { immediate: true },
  )

  return {
    // reactive state
    products,
    total,
    loading,
    error,
    activeFilterCount,
    filters,
    page,
    searchInput,
    // actions
    setFilter,
    setPage,
    resetFilters,
    reload: load,
  }
}
