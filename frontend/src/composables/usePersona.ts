import { shallowRef } from 'vue'
import { fetchPersonas, savePersona } from '@/lib/api'
import type { SkinPersona } from '@/lib/types'

/**
 * Persona selection with persistence. The legacy buildless UI stored the
 * active persona id under `skintellect_active_persona_id` (older installs:
 * `skinsort_active_persona_id`); both are read as fallbacks and the current
 * selection is written under the new `skintellect_persona_id` key.
 */
const PERSONA_KEY = 'skintellect_persona_id'
const LEGACY_KEYS = ['skintellect_active_persona_id', 'skinsort_active_persona_id']

const DEFAULT_PERSONA: SkinPersona = {
  id: 'uap',
  name: 'Universal Adult Sensitive & Acne',
  skin_type: 'sensitive',
  concerns: ['Acne', 'Redness'],
  goals: ['Barrier Repair', 'Acne Fighting'],
  exclude_fungal_acne_triggers: true,
  exclude_drying_alcohols: true,
  exclude_fragrance: true,
  custom_exclusions: [],
}

function savedPersonaId(): string | null {
  for (const key of [PERSONA_KEY, ...LEGACY_KEYS]) {
    try {
      const value = localStorage.getItem(key)
      if (value) return value
    } catch {
      return null
    }
  }
  return null
}

export function usePersona() {
  const personas = shallowRef<SkinPersona[]>([])
  const current = shallowRef<SkinPersona>({ ...DEFAULT_PERSONA })
  const loading = shallowRef(true)

  async function load() {
    try {
      const list = await fetchPersonas()
      if (list.length > 0) {
        personas.value = list
        const savedId = savedPersonaId()
        const match = (savedId && list.find(p => p.id === savedId))
          ?? list.find(p => p.id === DEFAULT_PERSONA.id)
          ?? list[0]
        if (match && (savedId || current.value.id === DEFAULT_PERSONA.id)) {
          current.value = match
        }
      }
    } catch (cause) {
      console.error('Failed to load personas', cause)
    } finally {
      loading.value = false
    }
  }

  function select(persona: SkinPersona) {
    current.value = persona
    try {
      localStorage.setItem(PERSONA_KEY, persona.id)
    } catch {
      /* storage unavailable — selection stays in-memory */
    }
  }

  async function saveCustom(persona: SkinPersona): Promise<SkinPersona> {
    const saved = await savePersona(persona)
    select(saved)
    if (!personas.value.some(p => p.id === saved.id)) {
      personas.value = [...personas.value, saved]
    }
    return saved
  }

  return { personas, current, loading, load, select, saveCustom }
}
