<script setup lang="ts">
import type { Product } from '@/lib/types'
import { inciNames } from '@/lib/utils'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Star,
  Sparkles,
  Plus,
  Check,
  Droplets,
  Layers,
  CheckCircle2,
} from 'lucide-vue-next'

const props = defineProps<{
  product: Product
  isCompared: boolean
}>()

const emits = defineEmits<{
  (e: 'toggle-compare', product: Product): void
  (e: 'open-copilot', product: Product): void
  (e: 'view-details', product: Product): void
}>()

function getMatchScoreColor(score: number): string {
  if (score >= 90) return 'text-[#12635a] bg-[#e5f5f2] border-[#12635a]/30'
  if (score >= 70) return 'text-[#245ba9] bg-[#eaf2ff] border-[#245ba9]/30'
  return 'text-[#805309] bg-[#fff4da] border-[#805309]/30'
}
</script>

<template>
  <Card
    class="flex flex-col justify-between hover:shadow-lg hover:border-primary/40 transition-all duration-200 relative overflow-hidden group bg-card border-border/80 rounded-2xl"
  >
    <!-- Top Status Banner -->
    <div class="px-5 pt-4 pb-2 flex items-center justify-between gap-2 border-b border-border/40 bg-muted/20">
      <!-- Verified INCI Status -->
      <div class="flex items-center gap-1.5">
        <Badge
          v-if="product.formula_status === 'verified_complete'"
          variant="verified"
          class="gap-1 text-[11px] font-semibold py-0.5 px-2"
        >
          <ShieldCheck class="w-3.5 h-3.5" />
          Verified INCI ({{ product.names?.length || product.ingredients?.length || 'Full' }})
        </Badge>
        <Badge
          v-else-if="product.formula_status === 'unverified'"
          variant="unknown"
          class="gap-1 text-[11px] py-0.5 px-2"
        >
          <HelpCircle class="w-3.5 h-3.5" />
          Unverified Formula
        </Badge>
        <Badge
          v-else
          variant="negative"
          class="gap-1 text-[11px] py-0.5 px-2"
        >
          Missing Formula
        </Badge>
      </div>

      <!-- Persona Match Score Badge -->
      <div>
        <div
          v-if="product.persona_match?.match_status === 'contraindicated'"
          class="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full border text-[#a63244] bg-[#fff0f2] border-[#a63244]/30"
          :title="product.persona_match.explanation"
        >
          <AlertTriangle class="w-3.5 h-3.5 shrink-0" />
          Contraindicated
        </div>
        <div
          v-else-if="product.persona_match?.score !== undefined"
          class="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full border"
          :class="getMatchScoreColor(product.persona_match.score)"
        >
          <CheckCircle2 class="w-3 h-3 shrink-0" />
          {{ product.persona_match.score }}% Fit
        </div>
        <div
          v-else-if="product.match_score !== undefined"
          class="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full border"
          :class="getMatchScoreColor(product.match_score)"
        >
          {{ product.match_score }}% Fit
        </div>
      </div>
    </div>

    <!-- Product Title & Brand Info -->
    <CardHeader class="pt-4 pb-2 px-5 cursor-pointer" @click="emits('view-details', product)">
      <div class="flex items-center justify-between gap-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
        <span>{{ product.brand }}</span>
        <span class="text-foreground font-extrabold px-1.5 py-0.5 rounded bg-muted/60 text-[11px]">
          {{ product.price_tier || '$$' }}
        </span>
      </div>
      <CardTitle class="line-clamp-2 text-base font-bold text-foreground group-hover:text-primary transition-colors leading-snug pt-1">
        {{ product.name }}
      </CardTitle>

      <!-- Rating and Reviews -->
      <div class="flex items-center gap-3 pt-1 text-xs text-muted-foreground">
        <span v-if="product.rating" class="flex items-center gap-1 font-semibold text-foreground">
          <Star class="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
          {{ product.rating.toFixed(1) }}
          <span class="text-muted-foreground font-normal">({{ product.review_count || 0 }} reviews)</span>
        </span>
        <span class="text-muted-foreground text-[11px]">
          {{ product.category_display || 'Moisturizer' }}
        </span>
      </div>
    </CardHeader>

    <!-- Ingredients & Safety Features -->
    <CardContent class="flex flex-col gap-3 py-2 px-5 flex-grow cursor-pointer" @click="emits('view-details', product)">
      <!-- Safety Badges Micro Strip -->
      <div class="flex flex-wrap gap-1.5 text-[10px]">
        <span
          v-if="product.fungal_acne_safe === 1"
          class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-semibold border border-emerald-200 dark:border-emerald-800"
        >
          Fungal Safe
        </span>
        <span
          v-if="product.fragrance_free === 1"
          class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-semibold border border-blue-200 dark:border-blue-800"
        >
          Fragrance-Free
        </span>
        <span
          v-if="product.alcohol_free === 1"
          class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 font-medium"
        >
          Alcohol-Free
        </span>
      </div>

      <!-- Key Actives Highlighted -->
      <div v-if="product.key_actives && product.key_actives.length > 0" class="flex flex-col gap-1">
        <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Key Actives</span>
        <div class="flex flex-wrap gap-1">
          <Badge
            v-for="active in product.key_actives.slice(0, 3)"
            :key="active"
            variant="secondary"
            class="text-[11px] font-medium"
          >
            {{ active }}
          </Badge>
          <span v-if="product.key_actives.length > 3" class="text-[10px] text-muted-foreground self-center pl-1">
            +{{ product.key_actives.length - 3 }} more
          </span>
        </div>
      </div>

      <!-- Formula INCI Excerpt -->
      <div v-else-if="inciNames(product).length > 0" class="flex flex-col gap-1">
        <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Formula Highlights</span>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="ing in inciNames(product).slice(0, 4)"
            :key="ing"
            class="text-[11px] px-1.5 py-0.5 rounded bg-muted/60 text-muted-foreground capitalize"
          >
            {{ ing }}
          </span>
        </div>
      </div>

      <!-- Contraindication Notice -->
      <div
        v-if="product.persona_match?.contraindications_found && product.persona_match.contraindications_found.length > 0"
        class="text-xs text-evidence-negative bg-evidence-negative-bg/60 border border-evidence-negative/30 p-2.5 rounded-lg flex items-start gap-2 mt-1"
      >
        <AlertTriangle class="w-4 h-4 shrink-0 text-evidence-negative mt-0.5" />
        <div>
          <span class="font-bold">Avoid:</span>
          {{ product.persona_match.contraindications_found.join(', ') }}
        </div>
      </div>
    </CardContent>

    <!-- Footer Actions -->
    <CardFooter class="pt-3 pb-4 px-5 border-t border-border/40 flex items-center justify-between gap-2 bg-muted/10">
      <Button
        :variant="isCompared ? 'default' : 'outline'"
        size="sm"
        class="h-8 text-xs gap-1.5 font-semibold"
        @click="emits('toggle-compare', product)"
      >
        <Check v-if="isCompared" class="w-3.5 h-3.5 text-primary-foreground" />
        <Plus v-else class="w-3.5 h-3.5" />
        {{ isCompared ? 'Compared' : 'Compare' }}
      </Button>

      <Button
        variant="ghost"
        size="sm"
        class="h-8 text-xs gap-1.5 text-primary font-semibold hover:text-primary hover:bg-primary/10"
        @click="emits('open-copilot', product)"
      >
        <Sparkles class="w-3.5 h-3.5 text-primary" />
        Ask Copilot
      </Button>
    </CardFooter>
  </Card>
</template>
