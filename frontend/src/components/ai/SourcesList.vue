<script setup lang="ts">
import type { CopilotCitation } from '@/lib/types'
import { Badge } from '@/components/ui/badge'
import { BookOpen } from 'lucide-vue-next'

/**
 * Sources pattern (shadcn-vue AI Elements): the set of sources an answer
 * rests on, each carrying its evidence id so the viewer can fetch the
 * verbatim excerpt via /api/evidence/{id}. Inline citation spans are not
 * rendered because the backend identifies evidence per answer, not per
 * claim; when the stream starts emitting per-claim evidence ids, inline
 * citation can be added on top of this component.
 */
defineProps<{
  citations: CopilotCitation[]
}>()

const emit = defineEmits<{
  (e: 'inspect', citation: CopilotCitation): void
}>()
</script>

<template>
  <div v-if="citations.length > 0" class="mt-4 pt-3 border-t border-border/60">
    <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block mb-1.5">
      Scientific & Catalog Evidence
    </span>
    <div class="flex flex-wrap gap-1.5">
      <Badge
        v-for="cit in citations"
        :key="cit.id"
        variant="source"
        class="cursor-pointer text-[11px] gap-1 hover:bg-blue-100 transition-colors font-semibold"
        @click="emit('inspect', cit)"
      >
        <BookOpen class="w-3 h-3" />
        {{ cit.title }}
      </Badge>
    </div>
  </div>
</template>
