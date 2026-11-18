<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { SpeedInsights } from '@vercel/speed-insights/vue'
import { Toaster, toast } from 'vue-sonner'
import { useRoute, useRouter } from 'vue-router'
import type { Product, SkinPersona } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import PersonaDrawer from '@/components/explore/PersonaDrawer.vue'
import ProductDetailModal from '@/components/explore/ProductDetailModal.vue'
import { usePersona } from '@/composables/usePersona'
import { useCompareTray } from '@/composables/useCompareTray'
import {
  Scale,
  LayoutGrid,
  Network,
  SlidersHorizontal,
  Sparkles,
  FlaskConical,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// Persona state (shared across views: header control, scoring, copilot context)
const {
  personas,
  current: currentPersona,
  load: loadPersonas,
  select: selectPersona,
  saveCustom: saveCustomPersona,
} = usePersona()

// Compare tray state (shared across explore, compare, and copilot views)
const {
  products: comparedProducts,
  add: addToTray,
  remove: removeFromCompare,
  clear: clearTray,
  restore: restoreTray,
} = useCompareTray({ personaId: computed(() => currentPersona.value.id) })

const personaDrawerOpen = ref(false)

// Operator consoles (/study, /progress) ship outside the nav in production
// builds; import.meta.env.DEV is statically true only under the dev server.
// The routes themselves stay deep-linkable for watching a preparation run.
const SHOW_OPS_SURFACES = import.meta.env.DEV

// Product Detail Modal State
const selectedProduct = ref<Product | null>(null)
const detailModalOpen = ref(false)

const activeTab = computed(() => String(route.name ?? 'explore'))

// One moulded-key tab recipe for all four triggers (zoom-out review: one source, no drift).
const tabTriggerClass =
  'gap-2 shrink-0 rounded-sm px-3 py-2 text-xs sm:text-sm font-medium transition-colors cursor-pointer min-h-[44px] sm:min-h-0 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:key-moulded'

function handleSelectPersona(p: SkinPersona) {
  selectPersona(p)
}

async function handleSaveCustomPersona(p: SkinPersona) {
  try {
    await saveCustomPersona(p)
    toast.success('Skin profile saved — matches recalculated.')
  } catch (e) {
    toast.error('Could not save the skin profile. Adjusting for this session only.')
    console.error('Persona save failed', e)
  }
}

async function toggleCompare(prod: Product) {
  const result = await addToTray(prod)
  if (result === 'limit') {
    toast.error('You can compare up to 4 formulations simultaneously.')
  }
}

function viewDetails(prod: Product) {
  selectedProduct.value = prod
  detailModalOpen.value = true
}

async function openCopilot(prod: Product) {
  const result = await addToTray(prod)
  if (result === 'limit') {
    toast.error('Compare tray is full (4). Remove one to add this product.')
  }
  // The copilot's product context IS the compare tray (product_ids on every
  // ask). Carry the triggering product through the route so the copilot
  // screen visibly acknowledges it instead of opening blank.
  router.push({ path: '/copilot', query: { product_id: String(prod.id) } })
}

function goToCopilot() {
  router.push('/copilot')
}

onMounted(() => {
  loadPersonas()
  restoreTray()
})

function onTabSelect(value: string | number) {
  const name = String(value)
  if (name !== activeTab.value) router.push({ name })
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground font-sans">
    <!-- Skip link: the navbar is the first Tab stop on every page; this is
         the one keyboard bypass. #main carries tabindex="-1" so focus lands
         there in Chrome and Safari (main is not natively focusable). -->
    <a
      href="#main"
      class="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-[60] focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground"
    >
      Skip to main content
    </a>
    <!-- Navbar Header: the manila bar (Furrow chrome) -->
    <header class="border-b bg-background sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        <!-- Brand Logo & Global Title -->
        <div class="flex items-center gap-3">
          <RouterLink to="/" class="flex items-center gap-3 min-w-0">
            <div class="size-10 rounded-sm bg-primary text-primary-foreground flex items-center justify-center">
              <FlaskConical class="size-5" aria-hidden="true" />
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <!-- Brand wordmark: a page's one h1 belongs to the routed view (the landing's headline). -->
                <p class="text-xl text-foreground truncate">Formulation Studio</p>
              </div>
              <p class="text-xs text-muted-foreground hidden sm:block">
                Universal Skin, Hair, Body & Makeup Formulation Intelligence
              </p>
            </div>
          </RouterLink>
        </div>

        <!-- Workspaces & Persona Control -->
        <div class="flex items-center gap-2 sm:gap-3 min-w-0">
          <nav class="hidden lg:flex items-center gap-1 text-xs text-muted-foreground mr-1">
            <RouterLink
              to="/research"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium whitespace-nowrap"
              title="Structured evidence search with quote explorer"
            >
              Evidence Search
            </RouterLink>
            <RouterLink
              v-if="SHOW_OPS_SURFACES"
              to="/study"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium whitespace-nowrap"
              title="Prepared study, references and quality checks"
            >
              Study
            </RouterLink>
            <RouterLink
              v-if="SHOW_OPS_SURFACES"
              to="/progress"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium whitespace-nowrap"
              title="Preparation and indexing status"
            >
              Data Progress
            </RouterLink>
          </nav>
          <Button
            variant="outline"
            size="sm"
            class="h-9 px-3.5 gap-2 font-medium rounded-sm cursor-pointer shrink min-w-0 max-w-[170px] lg:max-w-none"
            @click="personaDrawerOpen = true"
          >
            <SlidersHorizontal class="w-4 h-4" aria-hidden="true" />
            <span class="hidden md:inline text-xs">Profile:</span>
            <span class="text-xs truncate min-w-0 max-w-[110px] sm:max-w-[160px] lg:max-w-none text-foreground font-medium">
              {{ currentPersona.name }}
            </span>
          </Button>
        </div>
      </div>

      <!-- Navigation Tabs (router-driven; horizontally scrollable on small screens) -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 overflow-x-auto">
        <Tabs :model-value="activeTab" @update:model-value="onTabSelect">
          <TabsList class="h-11 bg-transparent p-0 gap-4 sm:gap-8 border-b-0">
            <TabsTrigger
              value="explore"
              :class="tabTriggerClass"
            >
              <LayoutGrid class="w-4 h-4" aria-hidden="true" />
              Catalog & Explore
            </TabsTrigger>

            <TabsTrigger
              value="compare"
              :class="tabTriggerClass"
            >
              <Scale class="w-4 h-4" aria-hidden="true" />
              Compare Matrix
              <span
                v-if="comparedProducts.length > 0"
                class="size-5 rounded-sm bg-primary text-primary-foreground text-[10px] flex items-center justify-center font-medium"
              >
                {{ comparedProducts.length }}
              </span>
            </TabsTrigger>

            <TabsTrigger
              value="graph"
              :class="tabTriggerClass"
            >
              <Network class="w-4 h-4" aria-hidden="true" />
              Ingredient Graph
            </TabsTrigger>

            <TabsTrigger
              value="copilot"
              :class="tabTriggerClass"
            >
              <Sparkles class="w-4 h-4" aria-hidden="true" />
              Research Copilot
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
    </header>

    <!-- Main Content Area (route-owned) -->
    <main
      id="main"
      tabindex="-1"
      class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full flex flex-col gap-6 focus:outline-none"
    >
      <RouterView v-slot="{ Component }">
        <component
          :is="Component"
          :persona-id="currentPersona.id"
          :compared-products="comparedProducts"
          @toggle-compare="toggleCompare"
          @view-details="viewDetails"
          @open-copilot="openCopilot"
          @remove="removeFromCompare"
          @clear-all="clearTray"
          @ask-copilot-compare="goToCopilot"
        />
      </RouterView>
    </main>

    <!-- Persona Drawer Modal -->
    <PersonaDrawer
      :open="personaDrawerOpen"
      :current-persona="currentPersona"
      :available-personas="personas"
      @update:open="(val: boolean) => personaDrawerOpen = val"
      @select-persona="handleSelectPersona"
      @save-custom-persona="handleSaveCustomPersona"
    />

    <!-- Deep Product Details Modal -->
    <ProductDetailModal
      :open="detailModalOpen"
      :product="selectedProduct"
      :current-persona="currentPersona"
      :is-compared="selectedProduct ? comparedProducts.some(p => p.id === selectedProduct?.id) : false"
      @update:open="(val: boolean) => detailModalOpen = val"
      @open-copilot="openCopilot"
      @toggle-compare="toggleCompare"
      @select-product="viewDetails"
    />

    <Toaster rich-colors theme="light" position="bottom-right" />

    <SpeedInsights />
  </div>
</template>
