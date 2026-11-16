<script setup lang="ts">
import type { CopilotStep } from '@/lib/types'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { CheckCircle2, ChevronDown, Circle, Clock, Loader2 } from 'lucide-vue-next'
import { ref, watch } from 'vue'

/**
 * Plan/Task pattern (shadcn-vue AI Elements): renders the workflow's task
 * list from the backend stream (`node_update` todo_list + final todo_list),
 * with progress counts. Replaces the hand-rolled checklist that was driven
 * by a client-side regex intent classifier.
 */
const props = defineProps<{
  steps: CopilotStep[]
  live?: boolean
}>()

const open = ref(false)

// Collapse while pending, expand on failure so the user can see what failed.
watch(
  () => props.steps.map(s => s.status).join(','),
  (statuses) => {
    if (statuses.includes('failed')) open.value = true
  },
)

const doneCount = () => props.steps.filter(s => s.status === 'completed').length
</script>

<template>
  <Collapsible v-if="steps.length > 0" v-model:open="open" class="mb-3">
    <CollapsibleTrigger as-child>
      <button
        type="button"
        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-[11px] font-medium bg-card hover:bg-secondary border border-border text-muted-foreground hover:text-foreground transition-colors cursor-pointer group"
        :title="open ? 'Hide the workflow plan' : 'Inspect the workflow plan and progress'"
      >
        <Clock class="w-3 h-3 text-foreground" />
        <span>{{ open ? 'Hide workflow plan' : `Workflow plan (${steps.length} steps)` }}</span>
        <ChevronDown class="w-3 h-3 text-muted-foreground transition-transform duration-(--duration-state)" :class="{ 'rotate-180': open }" />
      </button>
    </CollapsibleTrigger>

    <CollapsibleContent>
      <div class="mt-2 p-3 rounded-lg bg-card border text-xs space-y-1.5">
        <div class="font-medium text-muted-foreground text-[11px] mb-1 flex items-center justify-between">
          <span class="flex items-center gap-1.5">
            <Clock class="w-3.5 h-3.5 text-foreground" />
            Workflow Steps
          </span>
          <span class="text-[11px] font-normal text-muted-foreground">
            {{ doneCount() }} / {{ steps.length }} done
          </span>
        </div>
        <div v-for="(step, idx) in steps" :key="idx" class="flex items-center gap-2 text-xs">
          <CheckCircle2 v-if="step.status === 'completed'" class="w-3.5 h-3.5 text-evidence-verified shrink-0" />
          <Loader2 v-else-if="step.status === 'in_progress'" class="w-3.5 h-3.5 animate-spin text-foreground shrink-0" />
          <Circle v-else class="w-3.5 h-3.5 text-muted-foreground shrink-0" />
          <span :class="step.status === 'completed' ? 'text-foreground font-medium' : 'text-muted-foreground'">
            {{ step.task }}
          </span>
        </div>
      </div>
    </CollapsibleContent>
  </Collapsible>
</template>
