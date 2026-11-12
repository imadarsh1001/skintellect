import type { ReviewInsights } from './api'

/**
 * Evidence-summary semantics extracted from the legacy workspace.js so the
 * SPA views and tests/check_ui_semantics.js share one implementation. The
 * rules preserved from the legacy checks:
 *  - most-mentioned themes come from counts, never array order
 *  - counts retain the collected-review denominator ("5 of 10")
 *  - opposing sentiments are surfaced as differing experiences ("mixed")
 *  - a one-sided extracted sample never implies consensus
 *  - an empty extraction produces no invented highlights
 *  - aspect ids get readable labels without inheriting object properties
 */

export type SummaryTone = 'good' | 'info' | 'warning' | 'negative' | 'mixed'

export interface SummaryCard {
  aspect: string
  label: string
  mentioning: number
  denominator: number
  positive: number
  negative: number
  mixed: number
  tone: SummaryTone
}

const LABEL_OVERRIDES: Record<string, string> = {
  scent: 'Scent',
  texture: 'Texture & feel',
  hydration: 'Hydration',
  absorption: 'Absorption',
  irritation: 'Irritation',
  white_cast: 'White Cast',
  value: 'Value for money',
  packaging: 'Packaging',
}

export function aspectLabel(id: string): string {
  // Own-property read only: 'constructor' must label as a plain word.
  if (Object.prototype.hasOwnProperty.call(LABEL_OVERRIDES, id)) {
    return LABEL_OVERRIDES[id]
  }
  return id
    .split('_')
    .map(part => (part ? part.charAt(0).toUpperCase() + part.slice(1) : part))
    .join(' ')
}

export interface ObservationLike {
  aspect?: string
  topic?: string
  sentiment?: string
  span?: string
  quote?: string
  evidence_id?: string
}

export function observationAspect(observation: ObservationLike): string {
  return observation.aspect || observation.topic || 'unspecified'
}

export function observationSentiment(observation: ObservationLike): string {
  return observation.sentiment || 'unspecified'
}

/**
 * Combined theme + experience filter over observations. Non-mutating;
 * unlabeled sentiment stays discoverable under 'unspecified'.
 */
export function filterObservations<T extends ObservationLike>(
  observations: readonly T[],
  aspect = '',
  sentiment = '',
): T[] {
  return observations.filter(observation => {
    if (aspect && observationAspect(observation) !== aspect) return false
    if (sentiment && observationSentiment(observation) !== sentiment) return false
    return true
  })
}

export interface SummaryModel {
  cards: SummaryCard[]
  /** True when the extraction itself flags mixed experiences. */
  showsDifferingExperiences: boolean
  /** True when the analyzed sample cannot imply consensus. */
  oneSidedSample: boolean
}

export function buildSummaryModel(insights: Pick<ReviewInsights, 'unique_reviews' | 'gemini_reviews' | 'aspects'>): SummaryModel {
  const denominator = insights.unique_reviews ?? 0
  const cards: SummaryCard[] = [...(insights.aspects ?? [])]
    .sort((a, b) => b.mentioning_reviews - a.mentioning_reviews)
    .map(aspect => {
      const mixed = (aspect.positive_reviews > 0 && aspect.negative_reviews > 0) || aspect.mixed_reviews > 0
      const tone: SummaryTone = mixed
        ? 'mixed'
        : aspect.negative_reviews > 0
          ? 'negative'
          : aspect.positive_reviews > 0
            ? 'good'
            : 'info'
      return {
        aspect: aspect.aspect,
        label: aspectLabel(aspect.aspect),
        mentioning: aspect.mentioning_reviews,
        denominator,
        positive: aspect.positive_reviews,
        negative: aspect.negative_reviews,
        mixed: aspect.mixed_reviews,
        tone,
      }
    })

  return {
    cards,
    showsDifferingExperiences: cards.some(card => card.tone === 'mixed'),
    oneSidedSample: cards.length > 0 && (insights.gemini_reviews ?? 0) < denominator,
  }
}
