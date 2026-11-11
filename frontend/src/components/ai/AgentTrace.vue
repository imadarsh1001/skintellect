<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Activity,
  ChevronDown,
  Clock,
  Layers,
  Zap,
} from 'lucide-vue-next'

/**
 * Trace pattern (shadcn-vue AI Elements): the agent run's routing decision,
 * dispatch matrix, event timeline, and stage latencies, rendered from the
 * backend `trace` payload. Replaces the ~170-line hand-rolled debugger with
 * a reusable presentation component over the same contract.
 */
interface AgentTracePayload {
  intent_route?: string
  route_reason?: string
  activated_agents?: string[]
  bypassed_agents?: string[]
  agents_summary?: string
  events?: Array<Record<string, unknown>>
  stage_timings_ms?: Record<string, number>
  elapsed_ms?: number
}

const props = defineProps<{
  trace: AgentTracePayload
}>()

const open = defineModel<boolean>('open', { default: false })

const AGENTS = [
  { key: 'search_catalog', label: '1. Catalog Search' },
  { key: 'extract_reviews', label: '2. Review ABSA' },
  { key: 'find_alternatives', label: '3. Formula Twins' },
  { key: 'retrieve_references', label: '4. PubMed & FDA' },
]

function isAgentActive(agent: string) {
  return props.trace.activated_agents?.includes(agent) ?? false
}

function formatEventTime(iso?: string) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return iso
  }
}
</script>

<template>
  <Collapsible v-model:open="open" class="mt-4 pt-3.5 border-t border-border/60">
    <CollapsibleTrigger as-child>
      <button
        type="button"
        class="w-full flex items-center justify-between p-2 rounded-xl bg-background/90 hover:bg-background border border-border/70 transition-colors text-left text-xs cursor-pointer group shadow-2xs"
      >
        <div class="flex items-center gap-2 flex-wrap">
          <span class="flex items-center gap-1 font-bold text-amber-600 dark:text-amber-400">
            <Zap class="w-3.5 h-3.5 fill-current" />
            Agent Trace
          </span>
          <Badge variant="outline" class="text-[10px] py-0 px-1.5 uppercase font-mono font-bold bg-muted/50 border-border/80">
            Route: {{ trace.intent_route || 'auto' }}
          </Badge>
          <Badge
            :variant="((trace.activated_agents || []).length <= 2) ? 'verified' : 'source'"
            class="text-[10px] py-0 px-1.5 font-bold"
          >
            {{ (trace.activated_agents || []).length }} Active · {{ (trace.bypassed_agents || []).length }} Bypassed
          </Badge>
          <span v-if="trace.elapsed_ms" class="text-[10px] text-muted-foreground font-mono">
            {{ trace.elapsed_ms }}ms
          </span>
        </div>
        <div class="flex items-center gap-1 text-muted-foreground group-hover:text-foreground">
          <span class="text-[10px] font-semibold">{{ open ? 'Hide' : 'Inspect' }}</span>
          <ChevronDown class="w-3.5 h-3.5 transition-transform duration-200" :class="{ 'rotate-180': open }" />
        </div>
      </button>
    </CollapsibleTrigger>

    <CollapsibleContent>
      <div class="mt-2.5 p-3 rounded-xl border bg-card/95 text-xs flex flex-col gap-3 font-sans shadow-xs">
        <!-- Routing decision -->
        <div class="space-y-1">
          <div class="flex items-center justify-between text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
            <span class="flex items-center gap-1">
              <Activity class="w-3 h-3 text-primary" />
              Intent Router Decision
            </span>
            <span class="font-mono text-[10px] lowercase text-primary font-bold">{{ trace.intent_route }}</span>
          </div>
          <p class="text-[11px] text-foreground bg-muted/40 p-2.5 rounded-lg border border-border/50 font-mono leading-relaxed">
            {{ trace.route_reason || 'Route dynamically mapped from query intent patterns.' }}
          </p>
        </div>

        <!-- Dispatch matrix -->
        <div class="space-y-1.5">
          <div class="text-[11px] font-bold text-muted-foreground uppercase tracking-wider flex items-center justify-between">
            <span class="flex items-center gap-1">
              <Layers class="w-3 h-3 text-indigo-500" />
              Agent Dispatch Matrix
            </span>
            <span class="text-[10px] font-normal text-muted-foreground">
              {{ trace.agents_summary || 'Selective tool activation' }}
            </span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div
              v-for="agent in AGENTS"
              :key="agent.key"
              class="p-2 rounded-lg border flex items-center justify-between text-[11px]"
              :class="isAgentActive(agent.key) ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-950 dark:text-emerald-100 font-medium' : 'bg-muted/30 border-dashed border-border/60 text-muted-foreground'"
            >
              <span>{{ agent.label }}</span>
              <Badge
                :variant="isAgentActive(agent.key) ? 'verified' : 'outline'"
                class="text-[9px] py-0 px-1 font-mono uppercase"
              >
                {{ isAgentActive(agent.key) ? 'Active' : 'Bypassed' }}
              </Badge>
            </div>
          </div>
        </div>

        <!-- Event timeline -->
        <div v-if="trace.events && trace.events.length > 0" class="space-y-1.5">
          <div class="text-[11px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
            <Clock class="w-3 h-3 text-primary" />
            Event Audit Timeline ({{ trace.events.length }} events)
          </div>
          <ScrollArea class="h-48 rounded-lg border p-2.5 bg-muted/20 font-mono text-[10px]">
            <div class="space-y-1 pr-3">
              <div
                v-for="(evt, idx) in trace.events"
                :key="idx"
                class="flex items-start justify-between py-1 border-b border-border/30 last:border-0 gap-2"
              >
                <div class="flex items-center gap-1.5 min-w-0">
                  <span
                    class="w-1.5 h-1.5 rounded-full shrink-0"
                    :class="evt.action === 'executed' || evt.action === 'completed' ? 'bg-emerald-500' : evt.action === 'bypassed' ? 'bg-amber-400' : 'bg-primary'"
                  />
                  <span class="font-bold text-foreground truncate">{{ evt.stage }}</span>
                  <span class="text-muted-foreground truncate">
                    [{{ evt.action }}<template v-if="evt.reason">: {{ evt.reason }}</template><template v-if="evt.products_curated">: {{ evt.products_curated }} prods</template><template v-if="evt.candidates_found">: {{ evt.candidates_found }} found</template>]
                  </span>
                </div>
                <span class="text-muted-foreground shrink-0">{{ formatEventTime(evt.timestamp as string | undefined) }}</span>
              </div>
            </div>
          </ScrollArea>
        </div>

        <!-- Stage latencies -->
        <div
          v-if="trace.stage_timings_ms"
          class="flex items-center justify-between text-[10px] text-muted-foreground border-t border-border/40 pt-2 font-mono flex-wrap gap-2"
        >
          <div class="flex items-center gap-2">
            <span>Interpret: <strong>{{ trace.stage_timings_ms.interpret || 0 }}ms</strong></span>
            <span>·</span>
            <span>Search: <strong>{{ trace.stage_timings_ms.search || 0 }}ms</strong></span>
            <span>·</span>
            <span>Evidence: <strong>{{ trace.stage_timings_ms.evidence || 0 }}ms</strong></span>
            <span>·</span>
            <span>Synthesis: <strong>{{ trace.stage_timings_ms.synthesis || 0 }}ms</strong></span>
          </div>
          <div class="font-bold text-foreground">
            Total: {{ trace.stage_timings_ms.elapsed_ms || trace.elapsed_ms }}ms
          </div>
        </div>
      </div>
    </CollapsibleContent>
  </Collapsible>
</template>
