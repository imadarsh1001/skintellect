/**
 * Per-route head state for the SPA. Every route renders the same static
 * shell, so the router's afterEach keeps the document title, canonical URL
 * and og:url in sync on every navigation. Canonicals strip the query string:
 * filter state is transient (?domain=skin, ?page=2), so a filtered view
 * canonicalizes to its clean path and crawlers never see duplicate pages.
 */

const FALLBACK_ORIGIN = 'https://skintellect.vercel.app'

/** Find the tag or create + append it once, then apply the current value. */
function upsertHeadElement(
  selector: string,
  create: () => HTMLElement,
  apply: (el: HTMLElement) => void,
): void {
  let el = document.head.querySelector<HTMLElement>(selector)
  if (!el) {
    el = create()
    document.head.appendChild(el)
  }
  apply(el)
}

export function setRouteSeo(title: string, path: string): void {
  const url = `${window.location.origin || FALLBACK_ORIGIN}${path}`

  document.title = title

  upsertHeadElement(
    'link[rel="canonical"]',
    () => Object.assign(document.createElement('link'), { rel: 'canonical' }),
    (el) => el.setAttribute('href', url),
  )
  upsertHeadElement(
    'meta[property="og:url"]',
    () => {
      const meta = document.createElement('meta')
      meta.setAttribute('property', 'og:url')
      return meta
    },
    (el) => el.setAttribute('content', url),
  )
  upsertHeadElement(
    'meta[property="og:title"]',
    () => {
      const meta = document.createElement('meta')
      meta.setAttribute('property', 'og:title')
      return meta
    },
    (el) => el.setAttribute('content', title),
  )
}
