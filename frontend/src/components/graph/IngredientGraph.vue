<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Network, Table, Info, Search } from 'lucide-vue-next'

interface GraphNode {
  id: string
  name: string
  category: 'barrier' | 'hydrator' | 'soother' | 'active' | 'excipient'
  frequency: number
  x: number
  y: number
  role_description: string
}

interface GraphLink {
  source: string
  target: string
  weight: number
}

// Curated high-fidelity moisturizer ingredient network
const nodes = ref<GraphNode[]>([
  { id: 'ceramide-np', name: 'Ceramide NP', category: 'barrier', frequency: 84, x: 260, y: 150, role_description: 'Essential stratum corneum lipid reinforcing skin moisture barrier.' },
  { id: 'cholesterol', name: 'Cholesterol', category: 'barrier', frequency: 62, x: 340, y: 130, role_description: 'Physiological lipid that synergizes with ceramides and fatty acids in a 3:1:1 ratio.' },
  { id: 'fatty-acids', name: 'Fatty Acids (Stearic/Palmitic)', category: 'barrier', frequency: 71, x: 230, y: 220, role_description: 'Lipid components crucial for lamellar phase barrier organization.' },
  { id: 'glycerin', name: 'Glycerin', category: 'hydrator', frequency: 95, x: 420, y: 230, role_description: 'Gold-standard low-molecular-weight humectant that draws water into the epidermis.' },
  { id: 'hyaluronic-acid', name: 'Hyaluronic Acid / Sodium Hyaluronate', category: 'hydrator', frequency: 78, x: 480, y: 160, role_description: 'High molecular water-binding glycosaminoglycan providing intense surface plumping.' },
  { id: 'panthenol', name: 'Panthenol (Pro-Vitamin B5)', category: 'soother', frequency: 68, x: 360, y: 310, role_description: 'Calming provitamin that reduces transepidermal water loss and erythema.' },
  { id: 'niacinamide', name: 'Niacinamide (Vitamin B3)', category: 'active', frequency: 74, x: 500, y: 300, role_description: 'Multi-functional active that stimulates ceramide biosynthesis and calms inflammation.' },
  { id: 'allantoin', name: 'Allantoin', category: 'soother', frequency: 45, x: 270, y: 320, role_description: 'Keratolytic soothing agent that softens dry, flaky skin and mitigates irritation.' },
  { id: 'centella', name: 'Centella Asiatica (Madecassoside)', category: 'soother', frequency: 52, x: 190, y: 290, role_description: 'Potent botanical triterpene fraction that suppresses pro-inflammatory cytokines.' },
  { id: 'squalane', name: 'Squalane', category: 'barrier', frequency: 60, x: 380, y: 220, role_description: 'Biocompatible, non-greasy saturated emollient mirroring human sebum squalene.' },
  { id: 'dimethicone', name: 'Dimethicone', category: 'excipient', frequency: 82, x: 550, y: 210, role_description: 'Breathable silicone occlusive that locks in hydration without suffocating pores.' },
])

const links = ref<GraphLink[]>([
  { source: 'ceramide-np', target: 'cholesterol', weight: 4 },
  { source: 'ceramide-np', target: 'fatty-acids', weight: 3 },
  { source: 'ceramide-np', target: 'glycerin', weight: 5 },
  { source: 'glycerin', target: 'hyaluronic-acid', weight: 4 },
  { source: 'glycerin', target: 'panthenol', weight: 4 },
  { source: 'panthenol', target: 'allantoin', weight: 3 },
  { source: 'panthenol', target: 'centella', weight: 3 },
  { source: 'niacinamide', target: 'glycerin', weight: 4 },
  { source: 'niacinamide', target: 'ceramide-np', weight: 3 },
  { source: 'squalane', target: 'ceramide-np', weight: 3 },
  { source: 'squalane', target: 'cholesterol', weight: 2 },
  { source: 'dimethicone', target: 'glycerin', weight: 4 },
])

const selectedNode = ref<GraphNode | null>(nodes.value[0])
const viewMode = ref<'graph' | 'table'>('graph')
const searchQuery = ref('')

const filteredNodes = computed(() => {
  if (!searchQuery.value) return nodes.value
  const q = searchQuery.value.toLowerCase()
  return nodes.value.filter(n => n.name.toLowerCase().includes(q) || n.role_description.toLowerCase().includes(q))
})

function getCategoryColor(category: GraphNode['category']): string {
  switch (category) {
    case 'barrier': return '#12635a'
    case 'hydrator': return '#245ba9'
    case 'soother': return '#6843a8'
    case 'active': return '#0e6870'
    case 'excipient': return '#526277'
  }
}

function getNode(id: string): GraphNode | undefined {
  return nodes.value.find(n => n.id === id)
}
</script>

<template>
  <div class="flex flex-col gap-6 w-full">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4 border-b pb-4">
      <div>
        <h2 class="text-xl font-bold flex items-center gap-2">
          <Network class="w-5 h-5 text-primary" />
          Ingredient Relationship Graph & Co-Occurrence Network
        </h2>
        <p class="text-xs text-muted-foreground mt-0.5">
          Explore how barrier lipids, humectants, and anti-inflammatory actives pair in validated formulations.
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
          Interactive Graph
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

    <!-- Graph View -->
    <div v-if="viewMode === 'graph'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- SVG Canvas -->
      <Card class="lg:col-span-2 overflow-hidden bg-slate-900 border-slate-800 p-2 flex flex-col justify-center items-center relative">
        <div class="absolute top-4 left-4 z-10 flex gap-2 flex-wrap">
          <span class="text-[11px] px-2 py-0.5 rounded-full bg-[#12635a] text-white">Barrier Lipids</span>
          <span class="text-[11px] px-2 py-0.5 rounded-full bg-[#245ba9] text-white">Humectants</span>
          <span class="text-[11px] px-2 py-0.5 rounded-full bg-[#6843a8] text-white">Soothing Actives</span>
          <span class="text-[11px] px-2 py-0.5 rounded-full bg-[#526277] text-white">Occlusives</span>
        </div>

        <svg viewBox="100 80 500 300" class="w-full h-[400px] select-none">
          <!-- Links -->
          <g class="stroke-slate-700" stroke-linecap="round">
            <line
              v-for="(link, idx) in links"
              :key="idx"
              :x1="getNode(link.source)?.x"
              :y1="getNode(link.source)?.y"
              :x2="getNode(link.target)?.x"
              :y2="getNode(link.target)?.y"
              :stroke-width="link.weight"
              class="opacity-60 transition-opacity hover:opacity-100"
            />
          </g>

          <!-- Nodes -->
          <g v-for="node in nodes" :key="node.id" class="cursor-pointer group" @click="selectedNode = node">
            <circle
              :cx="node.x"
              :cy="node.y"
              :r="selectedNode?.id === node.id ? 22 : 17"
              :fill="getCategoryColor(node.category)"
              :stroke="selectedNode?.id === node.id ? '#ffffff' : 'rgba(255,255,255,0.4)'"
              :stroke-width="selectedNode?.id === node.id ? 3 : 1.5"
              class="transition-all duration-200"
            />
            <text
              :x="node.x"
              :y="node.y + 26"
              text-anchor="middle"
              fill="#e2e8f0"
              font-size="10"
              font-weight="600"
              class="pointer-events-none drop-shadow"
            >
              {{ node.name.split(' ')[0] }}
            </text>
          </g>
        </svg>
      </Card>

      <!-- Selected Node Dossier -->
      <Card class="flex flex-col justify-between">
        <CardHeader class="pb-3 border-b">
          <div class="flex items-center justify-between">
            <span class="text-[11px] uppercase tracking-wider font-semibold text-muted-foreground">
              {{ selectedNode?.category }} Active
            </span>
            <Badge variant="verified" class="text-xs">
              {{ selectedNode?.frequency }}% Moisturizers
            </Badge>
          </div>
          <CardTitle class="text-lg font-bold text-foreground mt-1">
            {{ selectedNode?.name }}
          </CardTitle>
        </CardHeader>

        <CardContent class="flex flex-col gap-4 py-4 text-xs">
          <div>
            <h4 class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider mb-1">
              Physiological Role
            </h4>
            <p class="text-foreground leading-relaxed text-sm">
              {{ selectedNode?.role_description }}
            </p>
          </div>

          <div class="border-t pt-3">
            <h4 class="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider mb-2">
              Common Synergistic Co-Ingredients
            </h4>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="link in links.filter(l => l.source === selectedNode?.id || l.target === selectedNode?.id)"
                :key="link.source + link.target"
                class="px-2 py-1 rounded bg-muted text-[11px] font-medium"
              >
                {{ getNode(link.source === selectedNode?.id ? link.target : link.source)?.name }}
              </span>
            </div>
          </div>
        </CardContent>

        <div class="p-4 border-t bg-muted/20 flex items-center gap-2 text-xs text-muted-foreground">
          <Info class="w-4 h-4 shrink-0 text-primary" />
          <span>Click any node in the graph to inspect formulation relationships.</span>
        </div>
      </Card>
    </div>

    <!-- Accessible Table View -->
    <Card v-else class="w-full">
      <CardHeader class="pb-3 border-b flex flex-row items-center justify-between">
        <CardTitle class="text-base font-semibold">Moisturizer Active Ingredients Index</CardTitle>
        <div class="relative w-64">
          <Search class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <input
            v-model="searchQuery"
            placeholder="Search ingredients..."
            class="h-8 w-full pl-8 pr-3 text-xs rounded-md border border-input bg-background"
          />
        </div>
      </CardHeader>
      <CardContent class="p-0 overflow-x-auto">
        <table class="w-full text-xs text-left">
          <thead class="bg-muted text-muted-foreground font-semibold uppercase text-[10px] tracking-wider">
            <tr>
              <th class="p-3">Ingredient</th>
              <th class="p-3">Functional Class</th>
              <th class="p-3">Presence in Formulas</th>
              <th class="p-3">Scientific Role</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="node in filteredNodes" :key="node.id" class="hover:bg-muted/40 transition-colors">
              <td class="p-3 font-semibold text-foreground">{{ node.name }}</td>
              <td class="p-3">
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-medium uppercase"
                  :style="{ backgroundColor: getCategoryColor(node.category) + '22', color: getCategoryColor(node.category) }"
                >
                  {{ node.category }}
                </span>
              </td>
              <td class="p-3 font-medium">{{ node.frequency }}%</td>
              <td class="p-3 text-muted-foreground max-w-md">{{ node.role_description }}</td>
            </tr>
          </tbody>
        </table>
      </CardContent>
    </Card>
  </div>
</template>
