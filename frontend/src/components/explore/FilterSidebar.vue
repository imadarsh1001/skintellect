<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, RotateCcw, Filter, Shield } from 'lucide-vue-next'

/**
 * Two-way filter contracts via defineModel; the explore view owns the
 * query state (URL), the sidebar only edits it. `reset` stays an event.
 */
const search = defineModel<string>('search', { required: true })
const category = defineModel<string>('category', { required: true })
const country = defineModel<string>('country', { required: true })
const goal = defineModel<string>('goal', { required: true })
const priceTier = defineModel<string>('priceTier', { required: true })
const fungalSafe = defineModel<boolean>('fungalSafe', { required: true })
const fragranceFree = defineModel<boolean>('fragranceFree', { required: true })
const oilFree = defineModel<boolean>('oilFree', { required: true })
const poreFree = defineModel<boolean>('poreFree', { required: true })
const minMatch = defineModel<number>('minMatch', { required: true })
const sortBy = defineModel<string>('sortBy', { required: true })

const emit = defineEmits<{ (e: 'reset'): void }>()

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
        @click="emit('reset')"
      >
        <RotateCcw class="w-3.5 h-3.5 mr-1" />
        Reset
      </Button>
    </div>

    <!-- Search Input -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Search Formulations</label>
      <div class="relative">
        <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          v-model="search"
          placeholder="Brand, product, active INCI..."
          class="pl-9 h-9 text-xs"
        />
      </div>
    </div>

    <!-- Sort Strategy -->
    <div class="flex flex-col gap-1.5">
      <label class="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Sort Results</label>
      <select
        v-model="sortBy"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
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
        v-model="category"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
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
        v-model="country"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
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
        v-model="goal"
        class="w-full h-9 px-3 rounded-lg border border-input bg-background text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
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
          @click="priceTier = pt.value"
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
          v-model="fungalSafe"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
        />
      </label>

      <label class="flex items-center justify-between py-1 text-xs cursor-pointer hover:text-foreground">
        <span class="flex items-center gap-1.5 font-medium">
          <span>🌸</span> Fragrance-Free
        </span>
        <input
          v-model="fragranceFree"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
        />
      </label>

      <label class="flex items-center justify-between py-1 text-xs cursor-pointer hover:text-foreground">
        <span class="flex items-center gap-1.5 font-medium">
          <span>💧</span> Oil-Free
        </span>
        <input
          v-model="oilFree"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
        />
      </label>

      <label class="flex items-center justify-between py-1 text-xs cursor-pointer hover:text-foreground">
        <span class="flex items-center gap-1.5 font-medium">
          <span>🚫</span> 0 Pore Cloggers
        </span>
        <input
          v-model="poreFree"
          type="checkbox"
          class="w-4 h-4 rounded text-primary focus:ring-primary border-input cursor-pointer"
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
        v-model.number="minMatch"
        type="range"
        min="0"
        max="95"
        step="5"
        class="w-full accent-primary cursor-pointer"
      />
      <div class="flex justify-between text-[10px] text-muted-foreground font-semibold">
        <span>0% (All)</span>
        <span>60%</span>
        <span>95% (Strict)</span>
      </div>
    </div>
  </aside>
</template>
