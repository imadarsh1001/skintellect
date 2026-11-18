<script setup lang="ts">
import { computed } from 'vue'
import type { Product } from '@/lib/types'
import { inciNames, keyActiveName, keyActiveIcon } from '@/lib/utils'
import { motionDurationMs, useCountUp } from '@/lib/motion'
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
  if (score >= 90) return 'text-evidence-verified bg-evidence-verified-bg border-evidence-verified/40'
  if (score >= 70) return 'text-evidence-source bg-evidence-source-bg border-evidence-source/40'
  return 'text-evidence-unknown bg-evidence-unknown-bg border-evidence-unknown/40'
}

// Dealt moment (group 3): the fit figure counts up to its computed value on
// arrival — the score reads as computed-from-persona, not stamped-from-
// nowhere. Duration comes from the theme token; reduced motion renders the
// final value instantly (see lib/motion.ts).
const cardScore = computed(() => props.product.persona_match?.score ?? props.product.match_score)
const displayScore = useCountUp(cardScore, motionDurationMs('--duration-moment'))

// A failed local icon disappears; the badge text carries the meaning.
function hideBrokenIcon(event: Event) {
  ;(event.target as HTMLImageElement).style.display = 'none'
}
</script>

<template>
  <Card
    class="flex flex-col justify-between hover:border-input transition-colors relative overflow-hidden group bg-card border-border rounded-lg"
  >
    <!-- Top Status Banner -->
    <div class="px-5 pt-4 pb-2 flex items-center justify-between gap-2 border-b border-border bg-muted/20">
      <!-- Verified INCI Status -->
      <div class="flex items-center gap-1.5">
        <Badge
          v-if="product.formula_status === 'verified_complete'"
          variant="verified"
          class="gap-1 text-[11px] font-medium py-0.5 px-2"
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
          class="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full border text-evidence-negative bg-evidence-negative-bg border-evidence-negative/40"
          :title="product.persona_match.explanation"
        >
          <AlertTriangle class="w-3.5 h-3.5 shrink-0" />
          Contraindicated
        </div>
        <div
          v-else-if="product.persona_match?.score !== undefined"
          class="inline-flex items-center gap-1 text-[11px] font-medium px-2.5 py-0.5 rounded-full border enter-rise-sm"
          :class="getMatchScoreColor(product.persona_match.score)"
          :title="product.persona_match.explanation"
        >
          <CheckCircle2 class="w-3 h-3 shrink-0" />
          {{ displayScore ?? cardScore }}% Fit
        </div>
        <div
          v-else-if="product.match_score !== undefined"
          class="inline-flex items-center gap-1 text-[11px] font-medium px-2.5 py-0.5 rounded-full border enter-rise-sm"
          :class="getMatchScoreColor(product.match_score)"
          :title="(product.match_reasons || []).join(' · ') || undefined"
        >
          {{ displayScore ?? cardScore }}% Fit
        </div>
      </div>
    </div>

    <!-- Product Title & Brand Info -->
    <CardHeader class="pt-4 pb-2 px-5 cursor-pointer" @click="emits('view-details', product)">
      <div class="flex items-center justify-between gap-2 text-xs font-medium text-muted-foreground">
        <span>{{ product.brand }}</span>
        <span class="text-foreground font-medium px-1.5 py-0.5 rounded bg-muted/60 text-[11px]">
          {{ product.price_tier || '$$' }}
        </span>
      </div>
      <CardTitle class="text-base font-medium text-foreground leading-snug pt-1">
        <button
          type="button"
          class="w-full text-left py-2 -my-2 font-medium text-foreground group-hover:text-foreground transition-colors cursor-pointer truncate"
          :title="product.name"
          :aria-label="product.name"
          @click.stop="emits('view-details', product)"
        >
          {{ product.name }}
        </button>
      </CardTitle>

      <!-- Rating and Reviews -->
      <div class="flex items-center gap-3 pt-1 text-xs text-muted-foreground">
        <span v-if="product.rating" class="flex items-center gap-1 font-medium text-foreground">
          <Star class="w-3.5 h-3.5 fill-primary text-foreground" />
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
      <div class="flex flex-wrap gap-1.5 text-[11px]">
        <span
          v-if="product.fungal_acne_safe === 1"
          class="px-2 py-0.5 rounded-full bg-evidence-verified-bg text-evidence-verified font-medium border border-evidence-verified/40 "
        >
          Fungal Safe
        </span>
        <span
          v-if="product.fragrance_free === 1"
          class="px-2 py-0.5 rounded-full bg-evidence-source-bg text-evidence-source font-medium border border-evidence-source/40 "
        >
          Fragrance-Free
        </span>
        <span
          v-if="product.alcohol_free === 1"
          class="px-2 py-0.5 rounded-full bg-evidence-unknown-bg text-evidence-unknown font-medium border border-evidence-unknown/40"
        >
          Alcohol-Free
        </span>
      </div>

      <!-- Key Actives Highlighted -->
      <div v-if="product.key_actives && product.key_actives.length > 0" class="flex flex-col gap-1">
        <span class="text-[11px] font-medium text-muted-foreground">Key Actives</span>
        <div class="flex flex-wrap gap-1">
          <Badge
            v-for="(active, i) in product.key_actives.slice(0, 3)"
            :key="i"
            variant="secondary"
            class="text-[11px] font-medium"
          >
            <!-- The data's own SVG, served locally; a failed load leaves a
                 name-only badge rather than any substitute icon. -->
            <img
              v-if="keyActiveIcon(active)"
              :src="keyActiveIcon(active)"
              alt=""
              decoding="async"
              class="size-3.5 shrink-0"
              @error="hideBrokenIcon"
            />
            {{ keyActiveName(active) }}
          </Badge>
          <span v-if="product.key_actives.length > 3" class="text-[11px] text-muted-foreground self-center pl-1">
            +{{ product.key_actives.length - 3 }} more
          </span>
        </div>
      </div>

      <!-- Formula INCI Excerpt -->
      <div v-else-if="inciNames(product).length > 0" class="flex flex-col gap-1">
        <span class="text-[11px] font-medium text-muted-foreground">Formula Highlights</span>
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
          <span class="font-medium">Avoid:</span>
          {{ product.persona_match.contraindications_found.join(', ') }}
        </div>
      </div>
    </CardContent>

    <!-- Footer Actions -->
    <CardFooter class="pt-3 pb-4 px-5 border-t border-border flex items-center justify-between gap-2 bg-muted/10">
      <Button
        :variant="isCompared ? 'default' : 'outline'"
        size="sm"
        class="h-8 text-xs gap-1.5 font-medium"
        @click="emits('toggle-compare', product)"
      >
        <Check v-if="isCompared" class="w-3.5 h-3.5 text-primary-foreground" />
        <Plus v-else class="w-3.5 h-3.5" />
        {{ isCompared ? 'Compared' : 'Compare' }}
      </Button>

      <Button
        variant="ghost"
        size="sm"
        class="h-8 text-xs gap-1.5 text-evidence-source font-medium hover:text-evidence-source hover:bg-evidence-source-bg"
        @click="emits('open-copilot', product)"
      >
        <Sparkles class="w-3.5 h-3.5 text-evidence-source" />
        Ask Copilot
      </Button>
    </CardFooter>
  </Card>
</template>
