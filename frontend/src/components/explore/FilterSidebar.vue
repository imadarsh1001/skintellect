<script setup lang="ts">
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Search, RotateCcw, Filter, Sliders, Shield } from 'lucide-vue-next'

const props = defineProps<{
  search: string
  category: string
  country: string
  goal: string
  priceTier: string
  fungalSafe: boolean
  fragranceFree: boolean
  oilFree: boolean
  poreFree: boolean
  minMatch: number
  sortBy: string
}>()

const emits = defineEmits<{
  (e: 'update:search', val: string): void
  (e: 'update:category', val: string): void
  (e: 'update:country', val: string): void
  (e: 'update:goal', val: string): void
  (e: 'update:priceTier', val: string): void
  (e: 'update:fungalSafe', val: boolean): void
  (e: 'update:fragranceFree', val: boolean): void
  (e: 'update:oilFree', val: boolean): void
  (e: 'update:poreFree', val: boolean): void
  (e: 'update:minMatch', val: number): void
  (e: 'update:sortBy', val: string): void
  (e: 'reset'): void
}>()

const priceTiers = [
  { label: 'All', value: 'all' },
  { label: '$', value: '$' },
  { label: '$$', value: '$$' },
  { label: '$$$', value: '$$$' },
  { label: '$$$$', value: '$$$$' },
]

const sortOptions = [
  { label: '🏆 Best Persona Match', value: 'composite_desc' },
  { label: '⚡ Highest Match %', value: 'match_desc' },
  { label: '⭐ Highest Rating', value: 'rating_desc' },
  { label: '💬 Most Reviews', value: 'reviews_desc' },
  { label: '💰 Price: Low to High', value: 'price_asc' },
  { label: '💎 Price: High to Low', value: 'price_desc' },
]

const categories = [
  { label: 'All Categories', value: 'all' },
  { label: '🧴 Moisturizers', value: 'Moisturizers' },
  { label: '✨ Serums', value: 'Serums' },
  { label: '💧 Toners', value: 'Toners' },
  { label: '🧼 Cleansers', value: 'Cleansers' },
  { label: '☀️ Sunscreens', value: 'Sunscreens' },
  { label: '🧴 Body Lotions', value: 'Body Lotions' },
  { label: '💆 Hair Masks', value: 'Hair Masks' },
]

const countries = [
  { label: '🌍 All Countries', value: 'all' },
  { label: '🇰🇷 South Korea (K-Beauty)', value: 'South Korea' },
  { label: '🇯🇵 Japan (J-Beauty)', value: 'Japan' },
  { label: '🇫🇷 France (French Pharmacy)', value: 'France' },
  { label: '🇺🇸 United States', value: 'United States' },
  { label: '🇮🇳 India', value: 'India' },
  { label: '🇩🇪 Germany', value: 'Germany' },
  { label: '🇬🇧 United Kingdom', value: 'United Kingdom' },
  { label: '🇨🇦 Canada', value: 'Canada' },
  { label: '🇦🇺 Australia', value: 'Australia' },
]

const goals = [
  { label: 'All Goals', value: 'all' },
  { label: '🛡️ Barrier Repair', value: 'barrier' },
  { label: '🌟 Dark Spots & Glow', value: 'brightening' },
  { label: '🌿 Texture & Calming', value: 'soothing' },
]

const activeFilterCount = computed(() => {
  let count = 0
  if (props.search.trim()) count++
  if (props.category !== 'all') count++
  if (props.country !== 'all') count++
  if (props.goal !== 'all') count++
  if (props.priceTier !== 'all') count++
  if (props.fungalSafe) count++
  if (props.fragranceFree) count++
  if (props.oilFree) count++
  if (props.poreFree) count++
  if (props.minMatch > 0) count++
  return count
})
</script>

<template>
  <aside class="flex flex-col gap-4 p-4 sm:p-5 rounded-2xl border bg-card shadow-xs w-full lg:w-80 shrink-0">
    <!-- Header with Reset Button -->
    <div class="flex items-center justify-between border-b pb-3">
      <div class="flex items-center gap-2 font-bold text-sm text-foreground">
        <Filter class="w-4 h-4 text-primary" />
        Formulation Filters
      </div>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-xs text-muted-foreground hover:text-foreground font-semibold cursor-pointer"
        @click="emits('reset')"
      >
        <RotateCcw class="w-3.5 h-3.5 mr-1" />
        Reset
        <span
          v-if="activeFilterCount > 0"
          class="ml-1 px-1.5 py-0.2 rounded-full bg-primary text-primary-foreground text-[10px] font-bold"
        >
          {{ activeFilterCount }}
        </span>
      </Button>
    </div>

    <!-- Search Input -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Search Formulations</label>
      <div class="relative">
        <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          :model-value="search"
          placeholder="Brand, product, active INCI..."
          class="pl-9 h-9 text-xs"
          @update:model-value="(v: string | number) => emits('update:search', String(v))"
        />
      </div>
    </div>

    <!-- Sort Strategy -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Sort Results</label>
      <select
        :value="sortBy"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
        @change="(e: any) => emits('update:sortBy', e.target.value)"
      >
        <option v-for="s in sortOptions" :key="s.value" :value="s.value">
          {{ s.label }}
        </option>
      </select>
    </div>

    <!-- Category Dropdown -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Category</label>
      <select
        :value="category"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
        @change="(e: any) => emits('update:category', e.target.value)"
      >
        <option v-for="c in categories" :key="c.value" :value="c.value">
          {{ c.label }}
        </option>
      </select>
    </div>

    <!-- Country / Origin Dropdown -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Origin / Beauty Heritage</label>
      <select
        :value="country"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
        @change="(e: any) => emits('update:country', e.target.value)"
      >
        <option v-for="co in countries" :key="co.value" :value="co.value">
          {{ co.label }}
        </option>
      </select>
    </div>

    <!-- Target Focus Goal -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Skin Focus Goal</label>
      <select
        :value="goal"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
        @change="(e: any) => emits('update:goal', e.target.value)"
      >
        <option v-for="g in goals" :key="g.value" :value="g.value">
          {{ g.label }}
        </option>
      </select>
    </div>

    <!-- Price Tier Filter -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Budget Tier</label>
      <div class="grid grid-cols-5 gap-1">
        <Button
          v-for="pt in priceTiers"
          :key="pt.value"
          :variant="priceTier === pt.value ? 'default' : 'outline'"
          size="sm"
          class="h-8 text-xs font-semibold px-1"
          @click="emits('update:priceTier', pt.value)"
        >
          {{ pt.label }}
        </Button>
      </div>
    </div>

    <!-- Safety & Exclusion Checkboxes -->
    <div class="flex flex-col gap-2 pt-3 border-t">
      <div class="flex items-center justify-between">
        <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Strict Exclusions</label>
        <Shield class="w-3.5 h-3.5 text-primary" />
      </div>

      <label class="flex items-center justify-between py-1 text-xs cursor-pointer hover:text-foreground">
        <span class="flex items-center gap-1.5 font-medium">
          <span>🍄</span> Fungal Acne Safe
        </span>
        <input
          :checked="fungalSafe"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
          @change="(e: any) => emits('update:fungalSafe', e.target.checked)"
        />
      </label>

      <label class="flex items-center justify-between py-1 text-xs cursor-pointer hover:text-foreground">
        <span class="flex items-center gap-1.5 font-medium">
          <span>🌸</span> Fragrance-Free
        </span>
        <input
          :checked="fragranceFree"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
          @change="(e: any) => emits('update:fragranceFree', e.target.checked)"
        />
      </label>

      <label class="flex items-center justify-between py-1 text-xs cursor-pointer hover:text-foreground">
        <span class="flex items-center gap-1.5 font-medium">
          <span>💧</span> Oil-Free
        </span>
        <input
          :checked="oilFree"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
          @change="(e: any) => emits('update:oilFree', e.target.checked)"
        />
      </label>

      <label class="flex items-center justify-between py-1 text-xs cursor-pointer hover:text-foreground">
        <span class="flex items-center gap-1.5 font-medium">
          <span>🚫</span> 0 Pore Cloggers
        </span>
        <input
          :checked="poreFree"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
          @change="(e: any) => emits('update:poreFree', e.target.checked)"
        />
      </label>
    </div>

    <!-- Minimum Persona Match Slider -->
    <div class="flex flex-col gap-1.5 pt-3 border-t">
      <div class="flex items-center justify-between">
        <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Min Persona Match</label>
        <span class="text-xs font-black text-primary">{{ minMatch }}%</span>
      </div>
      <input
        type="range"
        min="0"
        max="95"
        step="5"
        :value="minMatch"
        class="w-full accent-primary cursor-pointer"
        @input="(e: any) => emits('update:minMatch', Number(e.target.value))"
      />
      <div class="flex justify-between text-[10px] text-muted-foreground font-semibold">
        <span>0% (All)</span>
        <span>60%</span>
        <span>95% (Strict)</span>
      </div>
    </div>
  </aside>
</template>
