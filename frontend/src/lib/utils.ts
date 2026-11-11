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
