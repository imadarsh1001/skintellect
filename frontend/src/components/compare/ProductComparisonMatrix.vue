<script setup lang="ts">
import { computed } from 'vue'
import type { Product } from '@/lib/types'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ShieldCheck, AlertTriangle, HelpCircle, X, Sparkles, Scale } from 'lucide-vue-next'

const props = defineProps<{
  products: Product[]
}>()

const emits = defineEmits<{
  (e: 'remove', productId: number): void
  (e: 'clear-all'): void
  (e: 'ask-copilot-compare', products: Product[]): void
}>()

// Calculate shared ingredients across all compared products
const sharedIngredients = computed(() => {
  if (props.products.length < 2) return []
  const formulaSets = props.products.map(p => new Set((p.names || []).map(n => n.toLowerCase())))
  return Array.from(formulaSets[0]).filter(name => formulaSets.every(s => s.has(name)))
})

// Calculate unique ingredients for each product
function getUniqueIngredients(product: Product): string[] {
  const currentSet = new Set((product.names || []).map(n => n.toLowerCase()))
  const otherNames = new Set(
    props.products
      .filter(p => p.id !== product.id)
      .flatMap(p => (p.names || []).map(n => n.toLowerCase()))
  )
  return Array.from(currentSet).filter(name => !otherNames.has(name))
}
</script>

<template>
  <div class="flex flex-col gap-6 w-full">
    <!-- Comparison Header -->
    <div class="flex items-center justify-between flex-wrap gap-4 border-b pb-4">
      <div>
        <h2 class="text-xl font-bold flex items-center gap-2">
          <Scale class="w-5 h-5 text-primary" />
          Side-by-Side Formulation Matrix
        </h2>
        <p class="text-xs text-muted-foreground mt-0.5">
          Comparing INCI compositions, shared actives, unique ingredients, and persona compatibility.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <Button
          variant="default"
          size="sm"
          class="gap-1.5"
          @click="emits('ask-copilot-compare', products)"
        >
          <Sparkles class="w-4 h-4" />
          Analyze Comparison with Copilot
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="text-xs text-muted-foreground"
          @click="emits('clear-all')"
        >
          Clear Matrix
        </Button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="products.length === 0" class="py-16 text-center border rounded-xl bg-card">
      <Scale class="w-10 h-10 text-muted-foreground stroke-1 mx-auto mb-2" />
      <h3 class="font-semibold text-sm">No products selected for comparison</h3>
      <p class="text-xs text-muted-foreground max-w-sm mx-auto mt-1">
        Select "Compare" on 2 or more products from the catalog to see their side-by-side chemical difference.
      </p>
    </div>

    <div v-else class="flex flex-col gap-6">
      <!-- Shared Ingredients Banner -->
      <div v-if="sharedIngredients.length > 0" class="rounded-xl border border-evidence-verified/20 bg-evidence-verified-bg/50 p-4">
        <div class="flex items-center gap-2 text-evidence-verified font-semibold text-sm mb-2">
          <ShieldCheck class="w-4 h-4" />
          <span>{{ sharedIngredients.length }} Common Shared Ingredients Across All Selected:</span>
        </div>
        <div class="flex flex-wrap gap-1.5">
          <Badge
            v-for="ing in sharedIngredients"
            :key="ing"
            variant="verified"
            class="text-xs capitalize font-medium"
          >
            {{ ing }}
          </Badge>
        </div>
      </div>

      <!-- Comparison Columns Grid -->
      <div
        class="grid gap-4"
        :style="{ gridTemplateColumns: `repeat(${products.length}, minmax(280px, 1fr))` }"
      >
        <Card
          v-for="p in products"
          :key="p.id"
          class="flex flex-col justify-between relative border-t-4 border-t-primary"
        >
          <!-- Remove Button -->
          <button
            class="absolute right-3 top-3 p-1 rounded-full text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
            title="Remove from comparison"
            @click="emits('remove', p.id)"
          >
            <X class="w-4 h-4" />
          </button>

          <CardHeader class="pb-3 pr-8">
            <span class="text-xs uppercase font-semibold text-muted-foreground">{{ p.brand }}</span>
            <CardTitle class="text-base font-bold">{{ p.name }}</CardTitle>
            <div class="flex items-center gap-2 pt-1">
              <Badge
                v-if="p.persona_match?.match_status === 'match'"
                variant="verified"
                class="text-xs font-semibold"
              >
                {{ p.persona_match.score }}% Persona Fit
              </Badge>
              <Badge
                v-else-if="p.persona_match?.match_status === 'contraindicated'"
                variant="negative"
                class="text-xs gap-1 font-semibold"
              >
                <AlertTriangle class="w-3 h-3" />
                Contraindicated
              </Badge>
              <Badge v-else-if="p.match_score !== undefined" variant="verified" class="text-xs font-semibold">
                {{ p.match_score }}% Persona Fit
              </Badge>
              <Badge v-else variant="unknown" class="text-xs">
                Unknown Fit
              </Badge>
              <span class="text-xs font-bold text-foreground">{{ p.price_tier }}</span>
            </div>
          </CardHeader>

          <CardContent class="flex flex-col gap-4 text-xs">
            <!-- Formula Provenance -->
            <div class="flex flex-col gap-1 border-t pt-3">
              <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">Formula Provenance</span>
              <div class="flex items-center gap-1.5 font-medium">
                <ShieldCheck v-if="p.formula_status === 'verified_complete'" class="w-3.5 h-3.5 text-evidence-verified" />
                <HelpCircle v-else class="w-3.5 h-3.5 text-evidence-unknown" />
                <span class="capitalize">{{ p.formula_status?.replace('_', ' ') }}</span>
              </div>
            </div>

            <!-- Key Actives -->
            <div class="flex flex-col gap-1.5 border-t pt-3">
              <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">Key Actives</span>
              <div v-if="p.key_actives && p.key_actives.length > 0" class="flex flex-wrap gap-1">
                <Badge v-for="act in p.key_actives" :key="act" variant="secondary" class="text-[11px]">
                  {{ act }}
                </Badge>
              </div>
              <span v-else class="text-muted-foreground italic">No specialized actives tagged</span>
            </div>

            <!-- Unique Ingredients -->
            <div class="flex flex-col gap-1.5 border-t pt-3">
              <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">
                Unique Ingredients ({{ getUniqueIngredients(p).length }})
              </span>
              <div class="flex flex-wrap gap-1 max-h-48 overflow-y-auto pr-1">
                <span
                  v-for="u in getUniqueIngredients(p)"
                  :key="u"
                  class="text-[11px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 capitalize"
                >
                  {{ u }}
                </span>
                <span v-if="getUniqueIngredients(p).length === 0" class="text-muted-foreground italic">
                  None (complete subset of others)
                </span>
              </div>
            </div>

            <!-- Complete INCI Ingredient Count -->
            <div class="flex flex-col gap-1 border-t pt-3">
              <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">Total INCI Ingredients</span>
              <span class="font-bold text-foreground text-sm">{{ p.names?.length || 0 }} ingredients</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
