import { computed, shallowRef, watch, type Ref } from 'vue'
import { fetchProduct } from '@/lib/api'
import type { Product } from '@/lib/types'

/**
 * Compare tray with persistence and detail enrichment.
 *
 * Products added from the grid come from the list endpoint, which omits
 * `names` — the comparison matrix computes shared/unique ingredients from
 * full INCI lists, so every add fetches `/api/products/{id}` and merges the
 * detail payload into the tray entry (fetch-detail-on-add; at most 4 items).
 * The tray persists as product ids in localStorage and re-fetches details
 * on restore, so reloads and deep links keep the comparison intact.
 */
const TRAY_KEY = 'skintellect_compare_ids'

export type AddResult = 'added' | 'exists' | 'limit'

export function useCompareTray(options: { personaId: Readonly<Ref<string>>; max?: number }) {
  const max = options.max ?? 4
  const products = shallowRef<Product[]>([])
  const restoring = shallowRef(true)
  const ids = computed(() => products.value.map(p => p.id))

  async function enrich(prod: Product): Promise<Product> {
    if (prod.names && prod.names.length > 0) return prod
    try {
      const full = await fetchProduct(prod.id, options.personaId.value)
      return { ...prod, ...full }
    } catch {
      return prod // keep the list payload; the matrix renders honest zeros
    }
  }

  function persist() {
    try {
      localStorage.setItem(TRAY_KEY, JSON.stringify(ids.value))
    } catch {
      /* storage unavailable — tray stays in-memory */
    }
  }

  async function restore() {
    let stored: unknown = null
    try {
      stored = JSON.parse(localStorage.getItem(TRAY_KEY) ?? 'null')
    } catch {
      stored = null
    }
    if (Array.isArray(stored)) {
      const storedIds = stored.filter((v): v is number => typeof v === 'number').slice(0, max)
      const details = await Promise.allSettled(
        storedIds.map(id => fetchProduct(id, options.personaId.value)),
      )
      products.value = details
        .filter((r): r is PromiseFulfilledResult<Product> => r.status === 'fulfilled')
        .map(r => r.value)
    }
    restoring.value = false
  }

  watch(ids, persist)

  async function add(prod: Product): Promise<AddResult> {
    if (products.value.some(p => p.id === prod.id)) return 'exists'
    if (products.value.length >= max) return 'limit'
    const optimistic: Product = { ...prod }
    products.value = [...products.value, optimistic]
    const enriched = await enrich(prod)
    products.value = products.value.map(p => (p.id === prod.id ? enriched : p))
    return 'added'
  }

  function remove(productId: number) {
    products.value = products.value.filter(p => p.id !== productId)
  }

  function clear() {
    products.value = []
  }

  function has(productId: number) {
    return products.value.some(p => p.id === productId)
  }

  return { products, ids, restoring, add, remove, clear, has, restore }
}
