<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchCatalogStats, fetchProducts, type CatalogStats } from '@/lib/api'
import type { Product } from '@/lib/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  FileSearch,
  Scale,
  ShieldCheck,
  Sparkles,
  HelpCircle,
} from 'lucide-vue-next'

// The landing owns no persona or compare-tray state (both stay global in
// App.vue). Its only data is the catalog's own record, read from the same
// API the Explore view uses. Content facts come from README.md/PRODUCT.md;
// figures are always live, never hardcoded, and a failed fetch leaves the
// figure band and the record preview off the page instead of rendering an
// invented number or an empty ledger.
defineOptions({ inheritAttrs: false })

const stats = ref<CatalogStats | null>(null)
const sample = ref<Product[]>([])

onMounted(async () => {
  try {
    const [statsRes, productsRes] = await Promise.all([
      fetchCatalogStats(),
      fetchProducts({ limit: 3 }),
    ])
    stats.value = statsRes
    sample.value = productsRes.products
  } catch (cause) {
    console.error('Landing catalog data unavailable', cause)
  }
})

// Parsed INCI count when the list payload carries it; the badge drops the
// parenthetical rather than show a filler word in a figure slot.
function inciCount(p: Product): number {
  return p.names?.length || p.ingredients?.length || 0
}

// The surfaces, named and described with the app's own words
// (App.vue nav titles, PRODUCT.md promises 3 and 4, the 4-item tray limit).
// /study is an operator console: its card ships only in dev builds — the
// route itself stays deep-linkable in production.
const surfaces = [
  {
    href: '/research',
    title: 'Evidence Search',
    icon: FileSearch,
    description:
      'Reviews are evidence, not summaries: every insight carries its exact supporting text span.',
  },
  ...(import.meta.env.DEV
    ? [
        {
          href: '/study',
          title: 'Study',
          icon: BookOpen,
          description: 'Prepared study, references and quality checks.',
        },
      ]
    : []),
  {
    href: '/compare',
    title: 'Compare Matrix',
    icon: Scale,
    description: 'A tray matrix scoring up to four formulations side by side.',
  },
  {
    href: '/copilot',
    title: 'Research Copilot',
    icon: Sparkles,
    description: 'Multi-agent deliberation that shows its reasoning steps and sources.',
  },
]
</script>

<template>
  <div class="flex flex-col gap-12 sm:gap-16">
    <!-- Hero: the ruled ledger. Headline, one sentence, live record, two actions. -->
    <section class="pt-2 sm:pt-6">
      <h1 class="max-w-3xl text-4xl sm:text-5xl text-foreground">
        The formulation index that shows its work
      </h1>
      <p class="mt-4 max-w-2xl text-base sm:text-lg text-muted-foreground leading-relaxed">
        Scores, safety audits, and ingredient evidence attributed to real review text.
      </p>

      <div class="mt-6 flex flex-wrap items-center gap-3">
        <Button as-child size="lg" class="px-6">
          <RouterLink to="/explore">
            Explore formulations
            <ArrowRight class="size-4" aria-hidden="true" />
          </RouterLink>
        </Button>
        <Button as-child variant="outline" size="lg" class="px-6">
          <a
            href="https://github.com/imadarsh1001/skintellect"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
            <ArrowUpRight class="size-4" aria-hidden="true" />
          </a>
        </Button>
      </div>

      <!-- The field band: the accent carries the surface, ink carries the type.
           Figures stay unit-bearing ( Furrow voice: never a number without its unit ). -->
      <div
        v-if="stats"
        class="mt-10 grid grid-cols-1 gap-y-4 sm:grid-cols-3 sm:gap-y-0 sm:divide-x sm:divide-primary-foreground/25 rounded-xl overflow-hidden bg-primary text-primary-foreground"
      >
        <div class="px-6 py-5">
          <div class="font-mono text-2xl sm:text-3xl tabular-nums leading-none">
            {{ stats.total_products?.toLocaleString() ?? '' }}
          </div>
          <div class="mt-2 text-sm">indexed formulations</div>
        </div>
        <div class="px-6 py-5">
          <div class="font-mono text-2xl sm:text-3xl tabular-nums leading-none">
            {{ stats.enriched_products?.toLocaleString() ?? '' }}
          </div>
          <div class="mt-2 text-sm">with full INCI parsed</div>
        </div>
        <div class="px-6 py-5">
          <div class="font-mono text-2xl sm:text-3xl tabular-nums leading-none">
            {{ stats.total_ingredients?.toLocaleString() ?? '' }}
          </div>
          <div class="mt-2 text-sm">ingredient dossiers</div>
        </div>
      </div>
    </section>

    <!-- The book as an index: a ruled table of live catalog rows on the card sheet.
         With the catalog unreachable, the whole section stays off the page rather
         than show an empty ledger. -->
    <section v-if="sample.length > 0">
      <div class="flex items-baseline justify-between gap-4">
        <h2 class="text-2xl sm:text-3xl text-foreground">The book as an index</h2>
        <p class="hidden sm:block text-xs text-muted-foreground">live rows from the catalog</p>
      </div>
      <ul class="mt-4 border-t border-foreground">
        <li
          v-for="p in sample"
          :key="p.id"
          class="flex flex-wrap items-baseline gap-x-3 gap-y-1.5 py-3.5 border-b"
        >
          <span class="text-sm font-medium text-foreground">{{ p.name }}</span>
          <span class="text-xs text-muted-foreground">{{ p.brand }}</span>
          <span v-if="p.category_display" class="text-xs text-muted-foreground">
            {{ p.category_display }}
          </span>
          <span class="inline-flex items-center sm:ml-auto">
            <Badge v-if="p.formula_status === 'verified_complete'" variant="verified" class="gap-1 text-[11px]">
              <ShieldCheck class="w-3.5 h-3.5" aria-hidden="true" />
              Verified INCI{{ inciCount(p) ? ` (${inciCount(p)})` : '' }}
            </Badge>
            <Badge v-else-if="p.formula_status === 'unverified'" variant="unknown" class="gap-1 text-[11px]">
              <HelpCircle class="w-3.5 h-3.5" aria-hidden="true" />
              Unverified Formula
            </Badge>
          </span>
        </li>
      </ul>
      <RouterLink
        to="/explore"
        class="mt-4 inline-flex items-center gap-1.5 min-h-[44px] text-sm font-medium text-foreground hover:underline underline-offset-4"
      >
        Browse the full catalog
        <ArrowRight class="size-4" aria-hidden="true" />
      </RouterLink>
    </section>

    <!-- Four working surfaces, as notebook cards: entry radius, 1px ink ring. -->
    <section>
      <h2 class="text-2xl sm:text-3xl text-foreground">Four working surfaces</h2>
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <RouterLink
          v-for="s in surfaces"
          :key="s.href"
          :to="s.href"
          class="group rounded-xl border border-foreground/70 bg-card p-6 shadow-[var(--shadow-card)] transition-colors hover:bg-accent"
        >
          <div class="flex items-center gap-2.5">
            <component :is="s.icon" class="size-5 shrink-0" aria-hidden="true" />
            <h3 class="text-base font-medium text-foreground">{{ s.title }}</h3>
          </div>
          <p class="mt-2 text-sm text-muted-foreground leading-relaxed">{{ s.description }}</p>
        </RouterLink>
      </div>
    </section>
  </div>
</template>
