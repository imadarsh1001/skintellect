<script setup lang="ts">
import { ref } from 'vue'
import type { SkinPersona } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { SlidersHorizontal, Check, AlertCircle } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  currentPersona: SkinPersona
  availablePersonas: SkinPersona[]
}>()

const emits = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'select-persona', persona: SkinPersona): void
  (e: 'save-custom-persona', persona: SkinPersona): void
}>()

const skinTypes: Array<SkinPersona['skin_type']> = ['oily', 'dry', 'combination', 'sensitive', 'normal']
const commonGoals = ['Barrier Repair', 'Acne Fighting', 'Soothing / Anti-Redness', 'Deep Hydration', 'Anti-Aging', 'Brightening']

const editedPersona = ref<SkinPersona>({ ...props.currentPersona })

function selectExisting(p: SkinPersona) {
  editedPersona.value = { ...p }
  emits('select-persona', p)
  emits('update:open', false)
}

function onGoalsUpdate(next: unknown) {
  if (Array.isArray(next)) editedPersona.value.goals = next.map(String)
}

// reka single toggle-group deselects to undefined on re-click; the incumbent
// no-op'd on the active skin type, so non-string updates are ignored.
function setSkinType(v: unknown) {
  if (typeof v === 'string') editedPersona.value.skin_type = v as SkinPersona['skin_type']
}

function applyCustom() {
  emits('save-custom-persona', editedPersona.value)
  emits('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="(val: boolean) => emits('update:open', val)">
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2 text-xl font-bold">
          <SlidersHorizontal class="w-5 h-5 text-primary" />
          Skin Profile & Sensitivity Persona
        </DialogTitle>
        <DialogDescription>
          Customize your skin criteria. Contraindications are deterministically enforced; products with triggers will be clearly flagged.
        </DialogDescription>
      </DialogHeader>

      <div class="flex flex-col gap-6 py-4">
        <!-- Preset Selector -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Select Preset Profile</label>
          <div class="flex flex-wrap gap-2">
            <Button
              v-for="p in availablePersonas"
              :key="p.id"
              :variant="p.id === currentPersona.id ? 'default' : 'outline'"
              size="sm"
              class="rounded-full"
              @click="selectExisting(p)"
            >
              <Check v-if="p.id === currentPersona.id" class="w-3.5 h-3.5 mr-1 text-primary-foreground" />
              {{ p.name }}
            </Button>
          </div>
        </div>

        <!-- Skin Type Selection -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Skin Type</label>
          <ToggleGroup
            type="single"
            :model-value="editedPersona.skin_type"
            class="grid grid-cols-5 gap-2 w-full"
            @update:model-value="setSkinType"
          >
            <ToggleGroupItem
              v-for="st in skinTypes"
              :key="st"
              :value="st"
              class="h-8 px-3 text-xs capitalize data-[state=on]:bg-primary data-[state=on]:text-primary-foreground data-[state=on]:shadow-xs data-[state=off]:border data-[state=off]:bg-background hover:bg-accent"
            >
              {{ st }}
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        <!-- Target Goals -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Target Skincare Goals</label>
          <ToggleGroup
            type="multiple"
            :model-value="editedPersona.goals"
            class="flex flex-wrap gap-2"
            @update:model-value="onGoalsUpdate"
          >
            <ToggleGroupItem
              v-for="goal in commonGoals"
              :key="goal"
              :value="goal"
              class="h-auto rounded-full px-3 py-1.5 text-xs data-[state=on]:bg-primary data-[state=on]:text-primary-foreground data-[state=off]:border data-[state=off]:bg-background hover:bg-accent"
            >
              {{ goal }}
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        <!-- Strict Sensitivity & Contraindication Rules -->
        <div class="flex flex-col gap-3 rounded-lg border border-evidence-unknown/30 bg-evidence-unknown-bg/40 p-4">
          <div class="flex items-center gap-2">
            <AlertCircle class="w-4 h-4 text-evidence-unknown" />
            <h4 class="text-sm font-semibold text-evidence-unknown">Strict Ingredient Contraindications</h4>
          </div>
          <p class="text-xs text-muted-foreground">
            Enforces zero-tolerance contraindication filtering against cosmetic formulations.
          </p>

          <div class="flex flex-col gap-2.5 pt-1">
            <label class="flex items-center gap-3 cursor-pointer text-sm">
              <Switch id="persona-exclude-fungal" v-model="editedPersona.exclude_fungal_acne_triggers" />
              <span class="font-medium">Exclude Fungal Acne (Malassezia) Triggers</span>
            </label>

            <label class="flex items-center gap-3 cursor-pointer text-sm">
              <Switch id="persona-exclude-fragrance" v-model="editedPersona.exclude_fragrance" />
              <span class="font-medium">Exclude Fragrance & Essential Oils (Parfum, Linalool, Limonene)</span>
            </label>

            <label class="flex items-center gap-3 cursor-pointer text-sm">
              <Switch id="persona-exclude-alcohols" v-model="editedPersona.exclude_drying_alcohols" />
              <span class="font-medium">Exclude Drying Alcohols (Alcohol Denat, Ethanol, Isopropyl)</span>
            </label>
          </div>
        </div>
      </div>

      <DialogFooter class="flex sm:justify-between items-center w-full gap-2">
        <Button variant="ghost" size="sm" @click="emits('update:open', false)">Cancel</Button>
        <Button variant="default" size="sm" @click="applyCustom">Apply & Recalculate Matches</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
