import DOMPurify from 'dompurify'
import { marked } from 'marked'

marked.setOptions({
  gfm: true,
  breaks: true,
})

/**
 * Render assistant markdown to sanitized HTML. The backend contract used to
 * state "copilot markdown is trusted" and render raw v-html; per the Stage 4
 * trust-boundary decision the output is now sanitized with DOMPurify, so the
 * documented invariant is: copilot markdown is NOT trusted markup — model
 * output can carry prompt-injected content and must survive sanitization.
 * (This flips the invariant in frontend/EGM.md and components/research/EGM.md.)
 */
export function renderMarkdown(content?: string): string {
  if (!content) return ''
  try {
    const parsed = marked.parse(content) as string
    return DOMPurify.sanitize(parsed, { USE_PROFILES: { html: true } })
  } catch {
    return DOMPurify.sanitize(content)
  }
}
