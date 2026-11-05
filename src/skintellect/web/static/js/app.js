/**
 * Skintellect Studio - Reactive Application Core (Vue 3)
 */

const { createApp, ref, reactive, computed, onMounted, watch } = Vue;

const app = createApp({
  setup() {
    // ----------------------------------------------------
    // Metadata & Constants
    // ----------------------------------------------------
    const countryFlags = {
      'South Korea': '🇰🇷', 'Japan': '🇯🇵', 'France': '🇫🇷', 'United States': '🇺🇸',
      'India': '🇮🇳', 'Germany': '🇩🇪', 'United Kingdom': '🇬🇧', 'Canada': '🇨🇦',
      'Indonesia': '🇮🇩', 'Philippines': '🇵🇭', 'Vietnam': '🇻🇳', 'Malaysia': '🇲🇾',
      'Australia': '🇦🇺', 'Sweden': '🇸🇪', 'Hungary': '🇭🇺', 'Thailand': '🇹🇭',
      'Poland': '🇵🇱', 'Denmark': '🇩🇰', 'Brazil': '🇧🇷', 'International': '🌍'
    };

    const dupePresets = [
      { brand: 'Skinceuticals', name: 'C E Ferulic', label: 'SkinCeuticals C E Ferulic ($182)' },
      { brand: 'Drunk Elephant', name: 'Protini', label: 'Drunk Elephant Protini ($68)' },
      { brand: 'Tatcha', name: 'Dewy Skin', label: 'Tatcha Dewy Skin Cream ($70)' },
      { brand: 'Augustinus Bader', name: 'Rich Cream', label: 'Augustinus Bader The Rich Cream ($290)' },
      { brand: "Paula's Choice", name: '2% BHA', label: "Paula's Choice 2% BHA Liquid ($35)" }
    ];

    const formulaPresets = {
      abib: "Water, Houttuynia Cordata Extract, Glycerin, Methyl Trimethicone, Cetyl Ethylhexanoate, Butylene Glycol, Niacinamide, Dipotassium Glycyrrhizate, Panthenol, Sodium Hyaluronate, Hydrolyzed Hyaluronic Acid, Hyaluronic Acid, Ceramide NP, Beta-Glucan, Allantoin, 1,2-Hexanediol",
      anua_azelaic: "Water, Azelaic Acid, Dipropylene Glycol, Niacinamide, Butylene Glycol, Panthenol, Dipotassium Glycyrrhizate, Allantoin, Sodium Hyaluronate, Beta-Glucan, Betaine Salicylate, Zinc PCA, 1,2-Hexanediol",
      cerave: "Water, Glycerin, Cetearyl Alcohol, Caprylic/Capric Triglyceride, Cetyl Alcohol, Ceteareth-20, Petrolatum, Ceramide NP, Ceramide AP, Ceramide EOP, Phytosphingosine, Cholesterol, Sodium Hyaluronate, Carbomer, Dimethicone, Phenoxyethanol",
      cosrx_sun: "Water, Ethylhexyl Methoxycinnamate, Homosalate, Alcohol Denat, Ethylhexyl Salicylate, Dipropylene Glycol, Silica, Isoamyl p-Methoxycinnamate, Cyclopentasiloxane, Stearic Acid, Glyceryl Stearate, PEG-100 Stearate, Fragrance, Aloe Arborescens Leaf Extract"
    };

    // ----------------------------------------------------
    // State
    // ----------------------------------------------------
    const products = ref([]);
    const loading = ref(false);
    const total = ref(0);
    const page = ref(1);
    const limit = ref(35);
    const totalPages = ref(1);
    const stats = ref(null);

    const allPersonas = ref([]);
    const activePersonaId = ref(localStorage.getItem('skintellect_active_persona_id') || localStorage.getItem('skinsort_active_persona_id') || 'uap');
    const personaDropdownOpen = ref(false);

    const currentView = ref('catalog'); // 'catalog' | 'ingredients' | 'formula' | 'routine' | 'dupe'
    const activeDomain = ref('all'); // 'all' | 'skin' | 'hair' | 'body' | 'makeup'
    const domains = ref([]);
    const sources = ref([]);

    const filters = reactive({
      category: 'all',
      domain: 'all',
      price_tier: 'all',
      country: 'all',
      goal: 'all',
      min_match: 0,
      search: '',
      fungal_safe: false,
      fragrance_free: false,
      oil_free: false,
      pore_free: false,
      sort_by: 'composite_desc'
    });

    // ----------------------------------------------------
    // Ingredient Explorer State
    // ----------------------------------------------------
    const ingState = reactive({
      search: '',
      function: 'all',
      domain: 'all',
      comedogenicMax: null,
      fungalSafeOnly: false,
      activeOnly: false,
      page: 1,
      limit: 24,
      total: 0,
      totalPages: 1,
      items: [],
      loading: false
    });
    const availableFunctions = ref([]);
    const selectedIngredient = ref(null);
    const ingDetailLoading = ref(false);
    let ingSearchTimer = null;

    const routine = reactive({
      cleansers: null,
      toners: null,
      serums: null,
      moisturizers: null,
      sunscreens: null
    });

    const routineAnalysis = reactive({
      conflicts: [],
      synergies: [],
      total_price_tier: '--',
      avg_match_score: '--'
    });

    const compareList = ref([]);
    const comparedProducts = ref([]);
    const compareLoading = ref(false);

    const activeModal = ref(null); // 'product' | 'routine' | 'dupe' | 'persona' | 'formula' | 'compare'
    const selectedProduct = ref(null);
    const modalLoading = ref(false);
    const productModalTab = ref('safety');
    const reviewSkinFilter = ref('all');
    const ingSearch = ref('');

    const dupeTarget = ref(null);
    const dupes = ref([]);
    const dupeLoading = ref(false);

    const personaTab = ref('presets');
    const customPersona = reactive({
      username: '',
      label: '',
      skin_type: 'combination',
      sensitivity: 'slightly_sensitive',
      concerns: ['dark_spots', 'barrier_repair'],
      exclusions: {
        fungal_acne_safe: true,
        fragrance_free: true,
        alcohol_free: true,
        oil_free: false,
        pore_clogger_free: false
      }
    });

    const formulaInput = ref(formulaPresets.abib);
    const formulaResult = ref(null);
    const formulaLoading = ref(false);
    const formulaTab = ref('overview'); // 'overview' | 'audit' | 'skin_types' | 'concerns' | 'deck'
    const formulaIngSearch = ref('');

    // ----------------------------------------------------
    // AI Board & CSI Detective State
    // ----------------------------------------------------
    const agentTab = ref('board'); // 'board' | 'csi'
    const agentInputText = ref(formulaPresets.anua_azelaic);
    const agentQuestion = ref("Evaluate barrier safety, comedogenic load, and Malassezia tolerance.");
    const agentLoading = ref(false);
    const agentDeliberation = ref(null);
    const agentRounds = ref([]);
    const agentMeta = ref(null);

    // CSI State
    const csiProblems = ref("Water, Ethylhexyl Palmitate, Cetearyl Alcohol, Fragrance\nWater, Isopropyl Myristate, Coconut Oil");
    const csiSafes = ref("Water, Glycerin, Ceramide NP, Squalane\nWater, Centella Asiatica, Panthenol");
    const csiReaction = ref("breakouts_acne");
    const csiLoading = ref(false);
    const csiResult = ref(null);

    const copyFeedback = reactive({
      routine: false,
      personaJson: false,
      formulaLog: false
    });

    let searchTimer = null;
    let formulaTimer = null;

    // ----------------------------------------------------
    // Computed Properties
    // ----------------------------------------------------
    const activePersona = computed(() => {
      return allPersonas.value.find(p => p.id === activePersonaId.value || p.username === activePersonaId.value) || allPersonas.value[0] || {
        username: 'uap',
        label: 'Combination Skin (uap)',
        skin_type: 'combination',
        sensitivity: 'slightly_sensitive',
        description: 'Targeting barrier repair & dark spots without fungal triggers.'
      };
    });

    const routineCount = computed(() => {
      return Object.values(routine).filter(Boolean).length;
    });

    const activeFilterCount = computed(() => {
      let cnt = 0;
      if (filters.category !== 'all') cnt++;
      if (filters.price_tier !== 'all') cnt++;
      if (filters.country !== 'all') cnt++;
      if (filters.goal !== 'all') cnt++;
      if (filters.min_match > 0) cnt++;
      if (filters.search) cnt++;
      if (filters.fungal_safe) cnt++;
      if (filters.fragrance_free) cnt++;
      if (filters.oil_free) cnt++;
      if (filters.pore_free) cnt++;
      if (filters.sort_by !== 'composite_desc') cnt++;
      return cnt;
    });

    const filteredIngredients = computed(() => {
      if (!selectedProduct.value || !selectedProduct.value.ingredients) return [];
      const ings = selectedProduct.value.ingredients;
      if (!ingSearch.value.trim()) return ings;
      const q = ingSearch.value.trim().toLowerCase();
      return ings.filter(ing => {
        const name = (ing.name || '').toLowerCase();
        const func = (ing.function || '').toLowerCase();
        return name.includes(q) || func.includes(q);
      });
    });

    const filteredReviews = computed(() => {
      if (!selectedProduct.value || !selectedProduct.value.reviews) return [];
      if (reviewSkinFilter.value === 'all') return selectedProduct.value.reviews;
      return selectedProduct.value.reviews.filter(r => {
        const st = (r.reviewer_skin_type || '').toLowerCase();
        return st.includes(reviewSkinFilter.value.toLowerCase());
      });
    });

    const reviewSkinStats = computed(() => {
      if (!selectedProduct.value || !selectedProduct.value.reviews) return {};
      const revs = selectedProduct.value.reviews;
      const counts = { all: revs.length, combination: 0, sensitive: 0, oily: 0, dry: 0, normal: 0 };
      revs.forEach(r => {
        const st = (r.reviewer_skin_type || '').toLowerCase();
        if (st.includes('comb')) counts.combination++;
        else if (st.includes('sens')) counts.sensitive++;
        else if (st.includes('oil')) counts.oily++;
        else if (st.includes('dry')) counts.dry++;
        else if (st.includes('norm')) counts.normal++;
      });
      return counts;
    });

    const filteredFormulaIngredients = computed(() => {
      if (!formulaResult.value || !formulaResult.value.ingredients_breakdown) return [];
      const q = (formulaIngSearch.value || '').trim().toLowerCase();
      if (!q) return formulaResult.value.ingredients_breakdown;
      return formulaResult.value.ingredients_breakdown.filter(it => 
        (it.name || '').toLowerCase().includes(q) ||
        (it.function || '').toLowerCase().includes(q) ||
        (it.category_badge || '').toLowerCase().includes(q) ||
        (it.safety_status || '').toLowerCase().includes(q)
      );
    });

    // ----------------------------------------------------
    // Core Methods
    // ----------------------------------------------------
    const loadProducts = async () => {
      loading.value = true;
      try {
        const params = {
          page: page.value,
          limit: limit.value,
          category: filters.category,
          domain: filters.domain || 'all',
          price_tier: filters.price_tier,
          country: filters.country,
          goal: filters.goal,
          min_match: filters.min_match,
          search: filters.search,
          fungal_safe: filters.fungal_safe,
          fragrance_free: filters.fragrance_free,
          oil_free: filters.oil_free,
          pore_free: filters.pore_free,
          sort_by: filters.sort_by,
          persona_id: activePersonaId.value
        };

        const res = await API.fetchProducts(params);
        products.value = res.products || [];
        total.value = res.total || 0;
        totalPages.value = res.total_pages || 1;
      } catch (e) {
        console.error("Failed to load products:", e);
      } finally {
        loading.value = false;
      }
    };

    const debouncedSearch = () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        page.value = 1;
        loadProducts();
      }, 300);
    };

    const setCategory = (cat) => {
      filters.category = (filters.category === cat) ? 'all' : cat;
      page.value = 1;
      loadProducts();
    };

    const setPriceTier = (tier) => {
      filters.price_tier = (filters.price_tier === tier) ? 'all' : tier;
      page.value = 1;
      loadProducts();
    };

    const setGoal = (g) => {
      filters.goal = (filters.goal === g) ? 'all' : g;
      page.value = 1;
      loadProducts();
    };

    const toggleSafety = (key) => {
      filters[key] = !filters[key];
      page.value = 1;
      loadProducts();
    };

    const resetFilters = () => {
      filters.category = 'all';
      filters.price_tier = 'all';
      filters.country = 'all';
      filters.goal = 'all';
      filters.min_match = 0;
      filters.search = '';
      filters.fungal_safe = false;
      filters.fragrance_free = false;
      filters.oil_free = false;
      filters.pore_free = false;
      filters.sort_by = 'composite_desc';
      page.value = 1;
      loadProducts();
    };

    const prevPage = () => {
      if (page.value > 1) {
        page.value--;
        loadProducts();
        window.scrollTo({ top: 380, behavior: 'smooth' });
      }
    };

    const nextPage = () => {
      if (page.value < totalPages.value) {
        page.value++;
        loadProducts();
        window.scrollTo({ top: 380, behavior: 'smooth' });
      }
    };

    // ----------------------------------------------------
    // Domain & View Methods
    // ----------------------------------------------------
    const selectDomain = (domainId) => {
      activeDomain.value = domainId;
      filters.domain = domainId;
      filters.category = 'all';
      page.value = 1;
      loadProducts();
    };

    const switchView = (v) => {
      currentView.value = v;
      if (v === 'ingredients' && ingState.items.length === 0) {
        loadIngredients();
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // ----------------------------------------------------
    // Ingredient Explorer Methods
    // ----------------------------------------------------
    const loadIngredients = async () => {
      ingState.loading = true;
      try {
        const res = await API.fetchIngredients({
          search: ingState.search,
          function: ingState.function,
          domain: ingState.domain,
          comedogenic_max: ingState.comedogenicMax,
          fungal_safe_only: ingState.fungalSafeOnly,
          active_only: ingState.activeOnly,
          page: ingState.page,
          limit: ingState.limit
        });
        ingState.items = res.ingredients || [];
        ingState.total = res.total || 0;
        ingState.totalPages = res.total_pages || 1;
      } catch (e) {
        console.error("Failed to load ingredients:", e);
      } finally {
        ingState.loading = false;
      }
    };

    const debouncedIngSearch = () => {
      clearTimeout(ingSearchTimer);
      ingSearchTimer = setTimeout(() => {
        ingState.page = 1;
        loadIngredients();
      }, 300);
    };

    const setIngFunction = (func) => {
      ingState.function = (ingState.function === func) ? 'all' : func;
      ingState.page = 1;
      loadIngredients();
    };

    const setIngDomain = (dom) => {
      ingState.domain = (ingState.domain === dom) ? 'all' : dom;
      ingState.page = 1;
      loadIngredients();
    };

    const toggleIngSafety = (key) => {
      ingState[key] = !ingState[key];
      ingState.page = 1;
      loadIngredients();
    };

    const openIngredientDetailModal = async (ing) => {
      selectedIngredient.value = ing;
      activeModal.value = 'ingredient_detail';
      ingDetailLoading.value = true;
      try {
        const full = await API.fetchIngredientDetail(ing.id);
        selectedIngredient.value = full;
      } catch (e) {
        console.error("Error loading ingredient detail:", e);
      } finally {
        ingDetailLoading.value = false;
      }
    };

    const prevIngPage = () => {
      if (ingState.page > 1) {
        ingState.page--;
        loadIngredients();
      }
    };

    const nextIngPage = () => {
      if (ingState.page < ingState.totalPages) {
        ingState.page++;
        loadIngredients();
      }
    };

    // ----------------------------------------------------
    // Persona Methods
    // ----------------------------------------------------
    const applyPersona = async (pId) => {
      activePersonaId.value = pId;
      localStorage.setItem('skintellect_active_persona_id', pId);
      personaDropdownOpen.value = false;
      page.value = 1;
      await loadProducts();
      if (activeModal.value === 'routine') {
        analyzeRoutine();
      }
      if (activeModal.value === 'formula') {
        runFormulaAnalysis();
      }
    };

    const saveCustomPersona = async () => {
      if (!customPersona.username.trim()) {
        alert("Please enter a username for the persona.");
        return;
      }
      try {
        const payload = {
          username: customPersona.username.toLowerCase().replace(/[^a-z0-9_]/g, ''),
          label: customPersona.label.trim() || `${customPersona.username} (${customPersona.skin_type.toUpperCase()})`,
          description: `Custom profile: ${customPersona.skin_type} skin, ${customPersona.sensitivity.replace('_', ' ')}.`,
          skin_type: customPersona.skin_type,
          sensitivity: customPersona.sensitivity,
          target_concerns: [...customPersona.concerns],
          safety_exclusions: { ...customPersona.exclusions }
        };
        const saved = await API.createPersona(payload);
        allPersonas.value.push(saved);
        await applyPersona(saved.id);
        personaTab.value = 'presets';
        activeModal.value = null;
      } catch (e) {
        alert("Failed to save persona: " + e.message);
      }
    };

    const downloadPersonaJson = () => {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(allPersonas.value, null, 2));
      const a = document.createElement('a');
      a.setAttribute("href", dataStr);
      a.setAttribute("download", `skintellect_personas_${new Date().toISOString().slice(0, 10)}.json`);
      document.body.appendChild(a);
      a.click();
      a.remove();
    };

    const copyPersonaJson = () => {
      navigator.clipboard.writeText(JSON.stringify(allPersonas.value, null, 2)).then(() => {
        copyFeedback.personaJson = true;
        setTimeout(() => { copyFeedback.personaJson = false; }, 2000);
      });
    };

    // ----------------------------------------------------
    // Routine Methods
    // ----------------------------------------------------
    const getSlotKey = (p) => {
      const cat = (p.category_display || p.category || '').toLowerCase();
      if (cat.includes('cleanse')) return 'cleansers';
      if (cat.includes('tone')) return 'toners';
      if (cat.includes('sun') || cat.includes('spf')) return 'sunscreens';
      if (cat.includes('moistur') || cat.includes('cream') || cat.includes('oil')) return 'moisturizers';
      return 'serums';
    };

    const isInRoutine = (productId) => {
      return Object.values(routine).some(p => p && p.id === productId);
    };

    const toggleRoutine = async (p) => {
      const slot = getSlotKey(p);
      if (routine[slot] && routine[slot].id === p.id) {
        routine[slot] = null;
      } else {
        routine[slot] = p;
      }
      await analyzeRoutine();
    };

    const removeRoutineStep = (slot) => {
      routine[slot] = null;
      analyzeRoutine();
    };

    const clearRoutine = () => {
      routine.cleansers = null;
      routine.toners = null;
      routine.serums = null;
      routine.moisturizers = null;
      routine.sunscreens = null;
      routineAnalysis.conflicts = [];
      routineAnalysis.synergies = [];
      routineAnalysis.total_price_tier = '--';
      routineAnalysis.avg_match_score = '--';
    };

    const analyzeRoutine = async () => {
      const pIds = Object.values(routine).filter(Boolean).map(p => p.id);
      if (pIds.length === 0) {
        routineAnalysis.conflicts = [];
        routineAnalysis.synergies = [];
        routineAnalysis.total_price_tier = '--';
        routineAnalysis.avg_match_score = '--';
        return;
      }
      try {
        const res = await API.analyzeRoutine(pIds, activePersonaId.value);
        routineAnalysis.conflicts = res.conflicts || [];
        routineAnalysis.synergies = res.synergies || [];
        routineAnalysis.total_price_tier = res.total_price_tier || '$$';
        routineAnalysis.avg_match_score = `${res.avg_match_score || 0}%`;
      } catch (e) {
        console.error("Routine analysis error:", e);
      }
    };

    const copyRoutineMarkdown = () => {
      const stepLabels = {
        cleansers: 'Step 1: Cleanse (AM/PM)',
        toners: 'Step 2: Tone & Prep (AM/PM)',
        serums: 'Step 3: Target & Treat (AM/PM)',
        moisturizers: 'Step 4: Moisturize (AM/PM)',
        sunscreens: 'Step 5: Sun Protection (AM Only)'
      };
      const lines = Object.entries(routine).map(([k, p]) => {
        const label = stepLabels[k];
        if (p) {
          return `- **${label}:** [${p.brand} - ${p.name}](${p.url}) (${p.match_score}% Match, ${p.price_tier || '$$'})`;
        }
        return `- **${label}:** *(Empty Slot)*`;
      });
      const md = `### 🧴 My 5-Step Skincare Routine (${activePersona.value.label})\n\n${lines.join('\n')}\n\n*Built via Skintellect Studio*`;
      navigator.clipboard.writeText(md).then(() => {
        copyFeedback.routine = true;
        setTimeout(() => { copyFeedback.routine = false; }, 2000);
      });
    };

    // ----------------------------------------------------
    // Comparison Methods
    // ----------------------------------------------------
    const isInCompare = (productId) => {
      return compareList.value.includes(productId);
    };

    const toggleCompare = (p) => {
      const idx = compareList.value.indexOf(p.id);
      if (idx !== -1) {
        compareList.value.splice(idx, 1);
      } else {
        if (compareList.value.length >= 4) {
          alert("You can compare up to 4 formulations at once.");
          return;
        }
        compareList.value.push(p.id);
      }
    };

    const clearCompare = () => {
      compareList.value = [];
      comparedProducts.value = [];
    };

    const openCompareModal = async () => {
      if (compareList.value.length === 0) return;
      activeModal.value = 'compare';
      compareLoading.value = true;
      try {
        const prods = [];
        for (const pid of compareList.value) {
          const detail = await API.fetchProductDetail(pid, activePersonaId.value);
          prods.push(detail);
        }
        comparedProducts.value = prods;
      } catch (e) {
        console.error("Comparison load error:", e);
      } finally {
        compareLoading.value = false;
      }
    };

    // ----------------------------------------------------
    // Product Modal Methods
    // ----------------------------------------------------
    const openProductModal = async (p) => {
      selectedProduct.value = p;
      productModalTab.value = 'safety';
      reviewSkinFilter.value = 'all';
      ingSearch.value = '';
      activeModal.value = 'product';

      // If already fully enriched, we don't need a loader
      if (!p.ingredients || p.ingredients.length === 0) {
        modalLoading.value = true;
      }

      try {
        const enriched = await API.fetchProductDetail(p.id, activePersonaId.value);
        if (selectedProduct.value && selectedProduct.value.id === p.id) {
          selectedProduct.value = enriched;
        }
        // Cache enrichment on p object
        Object.assign(p, enriched);
      } catch (e) {
        console.warn("Could not enrich product detail:", e);
      } finally {
        modalLoading.value = false;
      }
    };

    // ----------------------------------------------------
    // Dupe Studio Methods
    // ----------------------------------------------------
    const openDupeModal = async (target = null) => {
      activeModal.value = 'dupe';
      if (target) {
        await loadDupesForProduct(target);
      } else if (products.value.length > 0) {
        const lux = products.value.find(p => (p.price_tier || '').length >= 3) || products.value[0];
        await loadDupesForProduct(lux);
      }
    };

    const loadDupesForProduct = async (p) => {
      dupeTarget.value = p;
      dupeLoading.value = true;
      dupes.value = [];
      try {
        const res = await API.fetchDupes(p.id);
        dupes.value = res.dupes || [];
      } catch (e) {
        dupes.value = p.similar_products || [];
      } finally {
        dupeLoading.value = false;
      }
    };

    const selectDupePreset = async (preset) => {
      try {
        const res = await API.fetchProducts({ search: `${preset.brand} ${preset.name}`, limit: 5 });
        if (res.products && res.products.length > 0) {
          await loadDupesForProduct(res.products[0]);
        } else {
          alert(`Product ${preset.label} was not found in catalog.`);
        }
      } catch (e) {
        alert("Error searching preset: " + e.message);
      }
    };

    // ----------------------------------------------------
    // Formula Lab Methods
    // ----------------------------------------------------
    const openFormulaLab = () => {
      activeModal.value = 'formula';
      if (!formulaResult.value && formulaInput.value) {
        runFormulaAnalysis();
      }
    };

    const loadFormulaPreset = (key) => {
      formulaInput.value = formulaPresets[key] || '';
      runFormulaAnalysis();
    };

    const runFormulaAnalysis = async () => {
      if (!formulaInput.value.trim()) {
        formulaResult.value = null;
        return;
      }
      formulaLoading.value = true;
      try {
        const res = await API.analyzeFormula(formulaInput.value, activePersonaId.value);
        formulaResult.value = res;
      } catch (e) {
        console.error("Formula analysis error:", e);
      } finally {
        formulaLoading.value = false;
      }
    };

    const copyFormulaAuditLog = () => {
      if (!formulaResult.value || !formulaResult.value.audit_log) return;
      const text = formulaResult.value.audit_log.join('\n');
      navigator.clipboard.writeText(text).then(() => {
        copyFeedback.formulaLog = true;
        setTimeout(() => { copyFeedback.formulaLog = false; }, 2000);
      });
    };

    // Auto-debounce formula input when user types
    watch(formulaInput, () => {
      clearTimeout(formulaTimer);
      formulaTimer = setTimeout(() => {
        if (activeModal.value === 'formula') {
          runFormulaAnalysis();
        }
      }, 500);
    });

    // ----------------------------------------------------
    // UI Helpers
    // ----------------------------------------------------
    const getFlag = (country) => {
      return countryFlags[country] || '📍';
    };

    const getPriceBadgeClass = (tier) => {
      if (tier === '$') return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      if (tier === '$$') return 'bg-blue-50 text-blue-800 border-blue-200';
      if (tier === '$$$') return 'bg-amber-50 text-amber-800 border-amber-200';
      return 'bg-purple-50 text-purple-800 border-purple-200';
    };

    // ----------------------------------------------------
    // AI Board & CSI Detective Methods
    // ----------------------------------------------------
    const openAiBoard = async (initialTab = 'board') => {
      agentTab.value = initialTab;
      activeModal.value = 'ai_board';
      if (!agentMeta.value) {
        try {
          agentMeta.value = await API.fetchAgentsMeta();
        } catch (e) {
          console.error("Failed to load agent meta:", e);
        }
      }
      if (initialTab === 'board' && !agentDeliberation.value) {
        await runAiBoardDeliberation();
      }
    };

    const runAiBoardDeliberation = async () => {
      if (!agentInputText.value.trim()) return;
      agentLoading.value = true;
      agentDeliberation.value = null;
      agentRounds.value = [];
      try {
        const res = await API.deliberateBoard(agentInputText.value, activePersonaId.value, agentQuestion.value);
        agentDeliberation.value = res;
        agentRounds.value = res.debate || [];
      } catch (e) {
        console.error("AI Board Deliberation Error:", e);
      } finally {
        agentLoading.value = false;
      }
    };

    const loadAgentPreset = (presetKey) => {
      if (formulaPresets[presetKey]) {
        agentInputText.value = formulaPresets[presetKey];
        runAiBoardDeliberation();
      }
    };

    const runCsiInvestigation = async () => {
      csiLoading.value = true;
      csiResult.value = null;
      try {
        const probs = csiProblems.value.split('\n').map(s => s.trim()).filter(Boolean);
        const safes = csiSafes.value.split('\n').map(s => s.trim()).filter(Boolean);
        const res = await API.investigateCsi(probs, safes, csiReaction.value);
        csiResult.value = res;
      } catch (e) {
        console.error("CSI Investigation Error:", e);
      } finally {
        csiLoading.value = false;
      }
    };

    const applyCsiExclusions = async (exclusions) => {
      if (!activePersona.value) return;
      const updatedExclusions = { ...activePersona.value.safety_exclusions };
      for (const ex of exclusions) {
        updatedExclusions[ex] = true;
      }
      try {
        await API.createPersona({
          username: activePersona.value.username,
          label: activePersona.value.label,
          description: (activePersona.value.description || '') + " (Tuned via CSI)",
          skin_type: activePersona.value.skin_type,
          sensitivity: activePersona.value.sensitivity,
          target_concerns: activePersona.value.target_concerns || [],
          safety_exclusions: updatedExclusions
        });
        const pers = await API.fetchPersonas();
        allPersonas.value = pers;
        applyPersona(activePersona.value.id);
        alert("✅ Persona safety exclusions successfully updated from CSI findings!");
      } catch (e) {
        console.error("Failed to apply exclusions:", e);
      }
    };

    const openAiBoardForProduct = (p) => {
      if (!p) return;
      const ings = (p.ingredients || []).map(i => typeof i === 'string' ? i : (i.name || '')).filter(Boolean).join(', ');
      if (ings) {
        agentInputText.value = ings;
        agentQuestion.value = `Evaluate formulation safety, vehicle stability and active compatibility for ${p.brand} ${p.name}`;
      }
      openAiBoard('board');
    };

    // Lifecycle
    onMounted(async () => {
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          activeModal.value = null;
          personaDropdownOpen.value = false;
        }
      });

      document.addEventListener('click', (e) => {
        const dd = document.getElementById('persona-dropdown-container');
        if (dd && !dd.contains(e.target)) {
          personaDropdownOpen.value = false;
        }
      });

      // Load initial personas, stats, domains & functions
      try {
        const [pers, st, doms, funcs] = await Promise.all([
          API.fetchPersonas(),
          API.fetchStats(),
          API.fetchDomains(),
          API.fetchIngredientFunctions()
        ]);
        allPersonas.value = pers;
        stats.value = st;
        domains.value = doms.domains || [];
        availableFunctions.value = funcs.functions || [];
      } catch (e) {
        console.warn("Bootstrap fetch error:", e);
      }

      await loadProducts();
    });

    return {
      // Constants
      countryFlags,
      dupePresets,
      formulaPresets,
      // State
      currentView,
      activeDomain,
      domains,
      sources,
      ingState,
      availableFunctions,
      selectedIngredient,
      ingDetailLoading,
      products,
      loading,
      total,
      page,
      limit,
      totalPages,
      stats,
      allPersonas,
      activePersonaId,
      activePersona,
      personaDropdownOpen,
      filters,
      routine,
      routineAnalysis,
      routineCount,
      activeFilterCount,
      compareList,
      comparedProducts,
      compareLoading,
      activeModal,
      selectedProduct,
      modalLoading,
      productModalTab,
      reviewSkinFilter,
      ingSearch,
      filteredIngredients,
      filteredReviews,
      reviewSkinStats,
      dupeTarget,
      dupes,
      dupeLoading,
      personaTab,
      customPersona,
      formulaInput,
      formulaResult,
      formulaLoading,
      formulaTab,
      formulaIngSearch,
      filteredFormulaIngredients,
      copyFeedback,
      // AI Board & CSI State
      agentTab,
      agentInputText,
      agentQuestion,
      agentLoading,
      agentDeliberation,
      agentRounds,
      agentMeta,
      csiProblems,
      csiSafes,
      csiReaction,
      csiLoading,
      csiResult,
      // Actions
      selectDomain,
      switchView,
      loadIngredients,
      debouncedIngSearch,
      setIngFunction,
      setIngDomain,
      toggleIngSafety,
      openIngredientDetailModal,
      prevIngPage,
      nextIngPage,
      loadProducts,
      debouncedSearch,
      setCategory,
      setPriceTier,
      setGoal,
      toggleSafety,
      resetFilters,
      prevPage,
      nextPage,
      applyPersona,
      saveCustomPersona,
      downloadPersonaJson,
      copyPersonaJson,
      isInRoutine,
      toggleRoutine,
      removeRoutineStep,
      clearRoutine,
      copyRoutineMarkdown,
      isInCompare,
      toggleCompare,
      clearCompare,
      openCompareModal,
      openProductModal,
      openDupeModal,
      loadDupesForProduct,
      selectDupePreset,
      openFormulaLab,
      loadFormulaPreset,
      runFormulaAnalysis,
      copyFormulaAuditLog,
      // AI Board & CSI Actions
      openAiBoard,
      openAiBoardForProduct,
      runAiBoardDeliberation,
      loadAgentPreset,
      runCsiInvestigation,
      applyCsiExclusions,
      getFlag,
      getPriceBadgeClass
    };
  }
});

app.mount('#app');
