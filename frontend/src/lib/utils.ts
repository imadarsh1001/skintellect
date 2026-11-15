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
 * /icons/key-actives/ (fetched by scripts/fetch_catalog_icons.py, with
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
  return localIconPath(url ?? '', 'key-actives')
}

/**
 * Map a scraped icon URL to its local copy under /icons/<family>/
 * (fetched by scripts/fetch_catalog_icons.py, manifest alongside).
 * .../icons/v2/<attribute>-<hash>.svg -> /icons/<family>/<attribute>.svg.
 * An unknown or empty URL yields '' and the caller renders no icon.
 */
export function localIconPath(url: string, family: 'key-actives' | 'ingredients'): string {
  if (!url) return ''
  const base = url.split('/').pop() ?? ''
  return '/icons/' + family + '/' + base.replace(/-[0-9a-f]{8,}\.svg$/, '.svg')
}

/** The benefit icons an ingredient payload carries ({name, alt, icon_url});
 *  at most three render, labeled by name (falling back to the payload's alt). */
export function ingredientBenefitIcons(
  ing: { icons?: Array<{ name?: string; alt?: string; icon_url?: string }> } | undefined,
): Array<{ src: string; title: string }> {
  return (ing?.icons ?? [])
    .slice(0, 3)
    .map(ic => ({ src: localIconPath(ic.icon_url ?? '', 'ingredients'), title: ic.name || ic.alt || '' }))
    .filter(ic => ic.src !== '' && ic.title !== '')
}
