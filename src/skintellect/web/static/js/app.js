/**
 * Skintellect Studio - Reactive Application Core (Vue 3)
 */

const { createApp, ref, reactive, computed, onMounted } = Vue;

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

    const currentView = ref('catalog'); // 'catalog' | 'ingredients'
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

    const compareList = ref([]);
    const comparedProducts = ref([]);
    const compareLoading = ref(false);

    const activeModal = ref(null); // 'product' | 'dupe' | 'persona' | 'compare'
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

    const copyFeedback = reactive({
      personaJson: false
    });

    let searchTimer = null;

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
      copyFeedback,
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
      isInCompare,
      toggleCompare,
      clearCompare,
      openCompareModal,
      openProductModal,
      openDupeModal,
      loadDupesForProduct,
      selectDupePreset,
      getFlag,
      getPriceBadgeClass
    };
  }
});

app.mount('#app');
