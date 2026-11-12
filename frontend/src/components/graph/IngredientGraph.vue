<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { Product, ProductConnections } from '@/lib/types'
import { fetchConnections } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { AlertTriangle, FlaskConical, Info, Loader2, Network, Scale, Table } from 'lucide-vue-next'

/**
 * Ingredient evidence graph backed by real data: for every product in the
 * compare tray, `/api/products/{id}/connections` returns recorded ingredient
 * nodes, related formulas sharing them, and references that discuss them —
 * each edge carrying its `evidence_id`. No pan/zoom/drag: the payload is a
 * small, readable evidence graph, and the accessible table is the primary
 * rendering for it.
 */
const props = defineProps<{
  products: Product[]
}>()

const viewMode = ref<'graph' | 'table'>('graph')
const connectionsByProduct = ref<Record<number, ProductConnections | 'error'>>({})
const loading = ref(false)

const trayIds = computed(() => props.products.map(p => p.id))
const idList = computed(() => trayIds.value.join(','))

watch(idList, () => {
  loadAll()
})

onMounted(() => {
  loadAll()
})

async function loadAll() {
  loading.value = trayIds.value.length > 0
  const results: Record<number, ProductConnections | 'error'> = { ...connectionsByProduct.value }
  for (const id of trayIds.value) delete results[id]
  await Promise.all(
    trayIds.value.map(async (id) => {
      try {
        results[id] = await fetchConnections(id, 5)
      } catch {
        results[id] = 'error'
      }
    }),
  )
  connectionsByProduct.value = results
  loading.value = false
}

function nodesOfType(conn: ProductConnections, type: ProductConnections['nodes'][number]['type']) {
  return conn.nodes.filter(n => n.type === type)
}

function connectionsFor(id: number): ProductConnections | null {
  const value = connectionsByProduct.value[id]
  return value && value !== 'error' ? value : null
}

function productById(id: number) {
  return props.products.find(p => p.id === id)
}

const NODE_STYLES: Record<ProductConnections['nodes'][number]['type'], { badge: string; label: string }> = {
  product: { badge: 'bg-primary/10 text-primary border-primary/30', label: 'Formula' },
  ingredient: { badge: 'bg-evidence-verified-bg text-evidence-verified border-evidence-verified/30', label: 'Recorded ingredient' },
  reference: { badge: 'bg-evidence-source-bg text-evidence-source border-evidence-source/30', label: 'Reference' },
}
</script>

<template>
  <div class="flex flex-col gap-6 w-full">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4 border-b pb-4">
      <div>
        <h2 class="text-xl font-bold flex items-center gap-2">
          <Network class="w-5 h-5 text-primary" />
          Ingredient Evidence Connections
        </h2>
        <p class="text-xs text-muted-foreground mt-0.5">
          Recorded ingredients, related formulas, and reference sources for everything in your compare tray.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button
          :variant="viewMode === 'graph' ? 'default' : 'outline'"
          size="sm"
          class="gap-1 text-xs"
          @click="viewMode = 'graph'"
        >
          <Network class="w-3.5 h-3.5" />
          Connections
        </Button>
        <Button
          :variant="viewMode === 'table' ? 'default' : 'outline'"
          size="sm"
          class="gap-1 text-xs"
          @click="viewMode = 'table'"
        >
          <Table class="w-3.5 h-3.5" />
          Accessible Table
        </Button>
      </div>
    </div>

    <!-- Empty state: nothing in the tray -->
    <div v-if="products.length === 0" class="py-16 text-center border rounded-xl bg-card">
      <Scale class="w-10 h-10 text-muted-foreground stroke-1 mx-auto mb-2" />
      <h3 class="font-semibold text-sm">No products selected</h3>
      <p class="text-xs text-muted-foreground max-w-sm mx-auto mt-1">
        Add products to the compare tray (Compare button on any catalog card) to inspect their
        recorded ingredient connections and the references behind them.
      </p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="py-16 flex items-center justify-center gap-2 text-xs text-muted-foreground">
      <Loader2 class="w-4 h-4 animate-spin" />
      Loading evidence connections...
    </div>

    <template v-else>
      <!-- Graph view: per-product evidence panels -->
      <div v-if="viewMode === 'graph'" class="flex flex-col gap-6">
        <template v-for="product in products" :key="product.id">
          <Card v-if="connectionsByProduct[product.id] === 'error'" class="p-4 flex items-start gap-2 text-xs">
            <AlertTriangle class="w-4 h-4 text-evidence-unknown shrink-0 mt-0.5" />
            <span>Connections for <strong>{{ product.brand }} {{ product.name }}</strong> could not be loaded.</span>
          </Card>

          <Card v-else-if="connectionsFor(product.id)" class="overflow-hidden">
            <CardHeader class="pb-3 border-b bg-muted/20">
              <div class="flex items-center justify-between gap-2">
                <div>
                  <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{{ product.brand }}</span>
                  <CardTitle class="text-base font-bold">{{ product.name }}</CardTitle>
                </div>
                <Badge variant="verified" class="text-[10px] shrink-0">
                  {{ connectionsFor(product.id)!.paths.length }} related formulas
                </Badge>
              </div>
            </CardHeader>

            <CardContent class="pt-4 flex flex-col gap-4 text-xs">
              <!-- Recorded ingredient nodes -->
              <div>
                <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">Recorded ingredients in evidence graph</span>
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <Badge
                    v-for="node in nodesOfType(connectionsFor(product.id)!, 'ingredient')"
                    :key="node.id"
                    variant="outline"
                    class="text-[11px] font-medium capitalize"
                    :class="NODE_STYLES.ingredient.badge"
                  >
                    {{ node.label.replace(/_/g, ' ') }}
                  </Badge>
                  <span
                    v-if="nodesOfType(connectionsFor(product.id)!, 'ingredient').length === 0"
                    class="text-muted-foreground italic"
                  >
                    No ingredient connections recorded for this product.
                  </span>
                </div>
              </div>

              <!-- Related formulas (paths) -->
              <div v-if="connectionsFor(product.id)!.paths.length > 0">
                <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">Related formulas sharing recorded ingredients</span>
                <div class="mt-2 space-y-1.5">
                  <div
                    v-for="path in connectionsFor(product.id)!.paths"
                    :key="path.product_id"
                    class="p-2.5 rounded-xl border bg-background/80 flex items-center justify-between gap-2"
                  >
                    <div>
                      <span class="font-bold text-foreground">{{ path.name }}</span>
                      <span class="text-muted-foreground ml-2 text-[11px]">
                        Shared: {{ path.shared_ingredients.join(', ') }}
                      </span>
                    </div>
                    <FlaskConical class="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                  </div>
                </div>
              </div>

              <!-- Reference nodes -->
              <div v-if="nodesOfType(connectionsFor(product.id)!, 'reference').length > 0">
                <span class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">References discussing these ingredients</span>
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <Badge
                    v-for="node in nodesOfType(connectionsFor(product.id)!, 'reference')"
                    :key="node.id"
                    variant="outline"
                    class="text-[11px] font-medium"
                    :class="NODE_STYLES.reference.badge"
                  >
                    {{ node.label }}
                  </Badge>
                </div>
              </div>

              <!-- Honest epistemics notice from the backend payload -->
              <div class="flex items-start gap-2 p-2.5 rounded-lg bg-muted/30 border text-[11px] text-muted-foreground">
                <Info class="w-3.5 h-3.5 shrink-0 mt-0.5 text-primary" />
                <span>{{ connectionsFor(product.id)!.notice }}</span>
              </div>
            </CardContent>
          </Card>
        </template>
      </div>

      <!-- Accessible table view -->
      <Card v-else class="w-full">
        <CardHeader class="pb-3 border-b">
          <CardTitle class="text-base font-semibold">Evidence edge table</CardTitle>
        </CardHeader>
        <CardContent class="p-0 overflow-x-auto">
          <table class="w-full text-xs text-left">
            <thead class="bg-muted text-muted-foreground font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th class="p-3">Product</th>
                <th class="p-3">Node</th>
                <th class="p-3">Type</th>
                <th class="p-3">Connected via</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <template v-for="product in products" :key="product.id">
                <template v-for="edge in connectionsFor(product.id)?.edges ?? []" :key="edge.from + edge.to">
                  <tr class="hover:bg-muted/40 transition-colors">
                    <td class="p-3 font-semibold text-foreground">{{ product.name }}</td>
                    <td class="p-3">{{ connectionsFor(product.id)!.nodes.find(n => n.id === edge.to)?.label ?? edge.to }}</td>
                    <td class="p-3">
                      <span
                        class="px-2 py-0.5 rounded-full text-[10px] font-medium uppercase"
                        :class="NODE_STYLES[connectionsFor(product.id)!.nodes.find(n => n.id === edge.to)?.type ?? 'ingredient'].badge"
                      >
                        {{ connectionsFor(product.id)!.nodes.find(n => n.id === edge.to)?.type ?? 'ingredient' }}
                      </span>
                    </td>
                    <td class="p-3 text-muted-foreground font-mono text-[11px]">{{ edge.relation }} · {{ edge.evidence_id }}</td>
                  </tr>
                </template>
              </template>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
