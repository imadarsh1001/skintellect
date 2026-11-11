<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Toaster, toast } from 'vue-sonner'
import { useRoute, useRouter } from 'vue-router'
import type { Product, SkinPersona } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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

// Product Detail Modal State
const selectedProduct = ref<Product | null>(null)
const detailModalOpen = ref(false)

const activeTab = computed(() => String(route.name ?? 'explore'))

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
  router.push('/copilot')
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
  <div class="min-h-screen flex flex-col bg-background text-foreground font-sans selection:bg-primary/20 selection:text-primary">
    <!-- Navbar Header -->
    <header class="border-b bg-card/85 backdrop-blur-md sticky top-0 z-40 shadow-xs">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        <!-- Brand Logo & Global Title -->
        <div class="flex items-center gap-3">
          <RouterLink to="/" class="flex items-center gap-3">
            <div class="size-10 rounded-xl bg-gradient-to-tr from-primary to-emerald-600 text-primary-foreground flex items-center justify-center font-black text-xl shadow-md">
              ✨
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h1 class="text-xl font-black tracking-tight text-foreground">Formulation Studio</h1>
                <Badge variant="verified" class="text-[10px] py-0.5 px-2 font-bold uppercase tracking-wider">
                  PRO · MULTI-DOMAIN
                </Badge>
              </div>
              <p class="text-[11px] text-muted-foreground hidden sm:block font-medium">
                Universal Skin, Hair, Body & Makeup Formulation Intelligence
              </p>
            </div>
          </RouterLink>
        </div>

        <!-- Workspaces & Persona Control -->
        <div class="flex items-center gap-2 sm:gap-3">
          <nav class="hidden lg:flex items-center gap-1 text-xs text-muted-foreground mr-1">
            <a
              href="/research"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium"
              title="Structured evidence workspace with quote explorer"
            >
              Evidence Workspace
            </a>
            <a
              href="/study"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium"
              title="3-product demonstration and reference study"
            >
              Study Demo
            </a>
            <a
              href="/progress"
              class="px-2.5 py-1 rounded-lg hover:bg-muted hover:text-foreground transition font-medium"
              title="Preparation and indexing status"
            >
              Data Progress
            </a>
          </nav>
          <Button
            variant="outline"
            size="sm"
            class="h-9 px-3.5 gap-2 border-primary/30 bg-primary/5 hover:bg-primary/10 text-primary font-semibold rounded-full shadow-xs cursor-pointer"
            @click="personaDrawerOpen = true"
          >
            <SlidersHorizontal class="w-4 h-4 text-primary" />
            <span class="hidden md:inline text-xs">Profile:</span>
            <span class="text-xs truncate max-w-[160px] text-foreground font-bold">
              {{ currentPersona.name }}
            </span>
          </Button>
        </div>
      </div>

      <!-- Navigation Tabs (router-driven) -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6">
        <Tabs :model-value="activeTab" @update:model-value="onTabSelect">
          <TabsList class="h-11 bg-transparent p-0 gap-8 border-b-0">
            <TabsTrigger
              value="explore"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <LayoutGrid class="w-4 h-4" />
              Catalog & Explore
            </TabsTrigger>

            <TabsTrigger
              value="compare"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <Scale class="w-4 h-4" />
              Compare Matrix
              <span
                v-if="comparedProducts.length > 0"
                class="size-5 rounded-full bg-primary text-primary-foreground text-[10px] flex items-center justify-center font-bold"
              >
                {{ comparedProducts.length }}
              </span>
            </TabsTrigger>

            <TabsTrigger
              value="graph"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <Network class="w-4 h-4" />
              Ingredient Graph
            </TabsTrigger>

            <TabsTrigger
              value="copilot"
              class="gap-2 rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-primary px-1 py-3 text-xs sm:text-sm font-semibold transition-colors cursor-pointer"
            >
              <Sparkles class="w-4 h-4 text-primary" />
              Research Copilot
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
    </header>

    <!-- Main Content Area (route-owned) -->
    <main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full flex flex-col gap-6">
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

    <Toaster rich-colors position="bottom-right" />
  </div>
</template>
