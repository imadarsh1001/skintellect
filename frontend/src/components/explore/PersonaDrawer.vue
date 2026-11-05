<script setup lang="ts">
import { ref } from 'vue'
import type { SkinPersona } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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

function toggleGoal(goal: string) {
  const index = editedPersona.value.goals.indexOf(goal)
  if (index >= 0) {
    editedPersona.value.goals.splice(index, 1)
  } else {
    editedPersona.value.goals.push(goal)
  }
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
          <div class="grid grid-cols-5 gap-2">
            <Button
              v-for="st in skinTypes"
              :key="st"
              :variant="editedPersona.skin_type === st ? 'default' : 'outline'"
              size="sm"
              class="capitalize"
              @click="editedPersona.skin_type = st"
            >
              {{ st }}
            </Button>
          </div>
        </div>

        <!-- Target Goals -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Target Skincare Goals</label>
          <div class="flex flex-wrap gap-2">
            <Badge
              v-for="goal in commonGoals"
              :key="goal"
              :variant="editedPersona.goals.includes(goal) ? 'default' : 'outline'"
              class="cursor-pointer px-3 py-1.5 text-xs transition-colors hover:bg-primary/20"
              @click="toggleGoal(goal)"
            >
              {{ goal }}
            </Badge>
          </div>
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
              <input
                v-model="editedPersona.exclude_fungal_acne_triggers"
                type="checkbox"
                class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
              />
              <span class="font-medium">Exclude Fungal Acne (Malassezia) Triggers</span>
            </label>

            <label class="flex items-center gap-3 cursor-pointer text-sm">
              <input
                v-model="editedPersona.exclude_fragrance"
                type="checkbox"
                class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
              />
              <span class="font-medium">Exclude Fragrance & Essential Oils (Parfum, Linalool, Limonene)</span>
            </label>

            <label class="flex items-center gap-3 cursor-pointer text-sm">
              <input
                v-model="editedPersona.exclude_drying_alcohols"
                type="checkbox"
                class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
              />
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
