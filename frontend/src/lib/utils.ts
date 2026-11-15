import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * The INCI name list for a product. No API payload carries a `names` array:
 * detail payloads carry `ingredients` objects (with name/function/safety
 * flags), list payloads carry neither. Everything that displays or diffs
 * ingredient lists goes through this helper so a single shape decision
 * stays in one place.
 */
export function inciNames(product: { names?: string[]; ingredients?: Array<{ name?: string }> }): string[] {
  if (product.names && product.names.length > 0) return product.names
  return (product.ingredients ?? [])
    .map(ing => ing.name)
    .filter((name): name is string => typeof name === 'string' && name.length > 0)
}

/**
 * Key-active entries arrive from the backend as {name, note, icon} objects
 * (parsed from key_actives_json, typed Any upstream), while synthetic and
 * seed payloads may carry plain strings. These helpers are the single shape
 * decision, like inciNames above. Icons live locally under
 * /icons/key-actives/ (fetched by scripts/fetch_key_active_icons.py, with
 * its manifest alongside); a missing icon yields '' and the caller falls
 * back to a lucide glyph instead of hotlinking the source host.
 */
export type KeyActive = { name?: string; note?: string; icon?: string } | string

export function keyActiveName(active: KeyActive): string {
  return (typeof active === 'string' ? active : active.name) ?? ''
}

export function keyActiveNote(active: KeyActive): string {
  return (typeof active === 'string' ? '' : active.note) ?? ''
}

export function keyActiveIcon(active: KeyActive): string {
  const url = typeof active === 'string' ? '' : active.icon
  if (!url) return ''
  // .../icons/v2/<attribute>-<hash>.svg -> /icons/key-actives/<attribute>.svg
  const base = url.split('/').pop() ?? ''
  return '/icons/key-actives/' + base.replace(/-[0-9a-f]{8,}\.svg$/, '.svg')
}
