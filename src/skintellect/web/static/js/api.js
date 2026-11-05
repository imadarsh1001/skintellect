/**
 * Centralized REST API Client for Skintellect FastAPI Backend
 */

const API = {
  baseUrl: '',

  async fetchProducts(params = {}) {
    const qs = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && val !== null && val !== '') {
        qs.append(key, val);
      }
    }
    const res = await fetch(`/api/products?${qs.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch products`);
    return await res.json();
  },

  async fetchProductDetail(id, personaId = 'uap') {
    const res = await fetch(`/api/products/${id}?persona_id=${encodeURIComponent(personaId)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch product details`);
    return await res.json();
  },

  async fetchPersonas() {
    const res = await fetch('/api/personas');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch personas`);
    return await res.json();
  },

  async createPersona(payload) {
    const res = await fetch('/api/personas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to create persona`);
    return await res.json();
  },

  async analyzeRoutine(productIds, personaId = 'uap') {
    const res = await fetch('/api/routine/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_ids: productIds, persona_id: personaId })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to analyze routine`);
    return await res.json();
  },

  async fetchDupes(productId) {
    const res = await fetch(`/api/dupes/${productId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch dupes`);
    return await res.json();
  },

  async analyzeFormula(ingredientsText, personaId = 'uap') {
    const res = await fetch('/api/formula-lab/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ingredients_text: ingredientsText, persona_id: personaId })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to analyze formula`);
    return await res.json();
  },

  async fetchStats() {
    const res = await fetch('/api/stats');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch stats`);
    return await res.json();
  },

  async fetchDomains() {
    const res = await fetch('/api/domains');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch domains`);
    return await res.json();
  },

  async fetchIngredients(params = {}) {
    const qs = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
      if (val !== undefined && val !== null && val !== '') {
        qs.append(key, val);
      }
    }
    const res = await fetch(`/api/ingredients?${qs.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch ingredients`);
    return await res.json();
  },

  async fetchIngredientDetail(id) {
    const res = await fetch(`/api/ingredients/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch ingredient detail`);
    return await res.json();
  },

  async fetchIngredientFunctions() {
    const res = await fetch('/api/ingredients/meta/functions');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch ingredient functions`);
    return await res.json();
  },

  async fetchAgentsMeta() {
    const res = await fetch('/api/agents/meta');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch agents meta`);
    return await res.json();
  },

  async deliberateBoard(ingredientsText, personaId = 'uap', userQuestion = '') {
    const res = await fetch('/api/agents/board/deliberate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ingredients_text: ingredientsText,
        persona_id: personaId,
        user_question: userQuestion
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to deliberate formula`);
    return await res.json();
  },

  async investigateCsi(problematicProducts, safeProducts, reactionType = 'breakouts_acne') {
    const res = await fetch('/api/agents/csi/investigate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        problematic_products: problematicProducts,
        safe_products: safeProducts,
        reaction_type: reactionType
      })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to investigate CSI`);
    return await res.json();
  }
};

window.API = API;
