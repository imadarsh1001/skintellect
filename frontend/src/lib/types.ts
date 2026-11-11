export type FormulaStatus = 'verified_complete' | 'unverified' | 'missing'

export interface Product {
  id: number
  brand: string
  name: string
  category?: string
  category_display?: string
  price_tier?: string
  url?: string
  image_url?: string
  description?: string
  ingredients?: Array<{ name: string; [key: string]: any }>
  names?: string[]
  complete?: boolean
  formula_status?: FormulaStatus
  is_seed?: number
  rating?: number
  review_count?: number
  reviews?: Array<{
    id: number
    product_id: number
    review_text: string
    reviewer_skin_type?: string
    date_posted?: string
    cleaned_text?: string
    aspects?: Array<{
      aspect: string
      sentiment: 'positive' | 'negative' | 'neutral'
      negated: boolean
      span: string
    }>
  }>
  skin_goals?: string[]
  key_actives?: string[]
  key_benefits?: string[]
  match_score?: number
  composite_score?: number
  match_reasons?: string[]
  fungal_acne_safe?: number
  fragrance_free?: number
  alcohol_free?: number
  oil_free?: number
  persona_match?: {
    is_match: boolean
    match_status: 'match' | 'contraindicated' | 'unknown'
    score: number
    contraindications_found: string[]
    matched_goals: string[]
    explanation: string
  }
}

export interface SkinPersona {
  id: string
  name: string
  skin_type: 'oily' | 'dry' | 'combination' | 'sensitive' | 'normal'
  concerns: string[]
  goals: string[]
  exclude_fungal_acne_triggers: boolean
  exclude_drying_alcohols: boolean
  exclude_fragrance: boolean
  custom_exclusions: string[]
  /** Raw backend fields (PersonaModel) preserved through the API adapter. */
  username?: string
  sensitivity?: string
  description?: string
  is_default?: number
}

export interface CatalogStats {
  total_products: number
  enriched_products: number
  total_reviews: number
  total_ingredients: number
  category_counts: Record<string, number>
  [key: string]: unknown
}

export interface ConnectionNode {
  id: string
  type: 'product' | 'ingredient' | 'reference'
  label: string
}

export interface ConnectionEdge {
  from: string
  to: string
  relation: 'recorded_contains' | 'discusses'
  evidence_id: string
}

export interface ConnectionPath {
  product_id: number
  name: string
  shared_ingredients: string[]
  evidence_ids: string[]
}

export interface ProductConnections {
  product_id: number
  nodes: ConnectionNode[]
  edges: ConnectionEdge[]
  paths: ConnectionPath[]
  notice: string
}

export interface PersonaEvaluation {
  product_id: number
  is_match: boolean
  match_status: 'match' | 'contraindicated' | 'unknown'
  score: number
  contraindications_found: string[]
  matched_goals: string[]
  missing_formula: boolean
  explanation: string
}

export interface IngredientGraphNode {
  id: string
  name: string
  role?: string
  frequency: number
  contraindicated?: boolean
}

export interface IngredientGraphLink {
  source: string
  target: string
  co_occurrence: number
}

export interface IngredientGraphData {
  nodes: IngredientGraphNode[]
  links: IngredientGraphLink[]
}

export interface CopilotStep {
  task: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
}

export interface CopilotToolCall {
  name: string
  args: Record<string, any>
  status: 'executing' | 'done' | 'failed'
}

export interface CopilotCitation {
  id: string
  title: string
  quote?: string
  url?: string
  source_kind: 'product' | 'review' | 'reference_note'
}

export interface ClarificationOption {
  id: string
  title: string
  description: string
  query: string
}

export interface ClarificationPayload {
  needs_clarification: boolean
  summary: string
  options: ClarificationOption[]
  allow_custom: boolean
}

export interface CopilotMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  todo_list?: CopilotStep[]
  tool_calls?: CopilotToolCall[]
  citations?: CopilotCitation[]
  matching_products?: any[]
  total_matches?: number
  review_insights?: any[]
  alternatives?: any[]
  clarification?: ClarificationPayload
  trace?: any
  showDebugger?: boolean
  showPlan?: boolean
  showCustomClarification?: boolean
  customClarificationText?: string
  streamingStage?: string
  timestamp: string
}
