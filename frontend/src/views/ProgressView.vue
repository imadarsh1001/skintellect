<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useIntervalFn } from '@vueuse/core'
import {
  cancelPreparationJob,
  fetchDemo,
  fetchProgress,
  submitPreparationJob,
  type DemoReadiness,
  type PreparationJobRow,
  type ProgressSnapshot,
} from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Loader2, RefreshCw, XCircle } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

/** SPA fold-in of the legacy /progress page: Gemini preparation jobs
 * (submit / cancel / poll) and coverage dashboards. Polls every 5 s only
 * while the page is visible, like the legacy page did. */

const progress = ref<ProgressSnapshot | null>(null)
const demo = ref<DemoReadiness | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const submitting = ref(false)

const form = reactive({
  kind: 'reviews' as 'reviews' | 'embed',
  limit: 20,
  product_id: '' as string,
  max_calls: 8,
  max_seconds: 120,
})

let loadInFlight = false

async function load() {
  if (loadInFlight) return // the 5s poll must not pile up behind a slow snapshot
  loadInFlight = true
  try {
    const [snapshot, demoRes] = await Promise.all([fetchProgress(), fetchDemo()])
    progress.value = snapshot
    demo.value = demoRes
    error.value = null
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : String(cause)
  } finally {
    loadInFlight = false
    loading.value = false
  }
}

onMounted(load)

const { pause, resume } = useIntervalFn(
  () => {
    if (document.visibilityState === 'visible') load()
  },
  5000,
)
// (pause/resume kept for clarity; polling pauses automatically while hidden.)

async function submitJob() {
  if (submitting.value) return
  submitting.value = true
  try {
    await submitPreparationJob({
      kind: form.kind,
      limit: form.limit,
      product_id: form.product_id ? Number(form.product_id) : null,
      max_calls: form.max_calls,
      max_seconds: form.max_seconds,
    })
    toast.success('Preparation job queued. Progress updates every few seconds.')
    await load()
  } catch (cause) {
    toast.error(cause instanceof Error ? cause.message : String(cause))
  } finally {
    submitting.value = false
  }
}

async function cancelJob(job: PreparationJobRow) {
  try {
    const result = await cancelPreparationJob(job.id)
    toast.info(result.notice || 'Cancellation requested.')
    await load()
  } catch (cause) {
    toast.error(cause instanceof Error ? cause.message : String(cause))
  }
}

function percent(processed: number, eligible: number): number {
  if (!eligible) return 0
  return Math.min(100, Math.round((processed / eligible) * 100))
}

const activeJobs = computed(() => (progress.value?.jobs ?? []).filter(j => ['queued', 'running', 'paused'].includes(j.status)))
const finishedJobs = computed(() => (progress.value?.jobs ?? []).filter(j => !['queued', 'running', 'paused'].includes(j.status)))

const STATUS_VARIANT: Record<string, 'verified' | 'source' | 'unknown' | 'negative' | 'outline'> = {
  completed: 'verified',
  running: 'source',
  queued: 'source',
  paused: 'unknown',
  interrupted: 'unknown',
  failed: 'negative',
  cancelled: 'outline',
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="border-b pb-4 flex items-start justify-between flex-wrap gap-3">
      <div>
        <span class="text-[11px] font-bold uppercase tracking-wider text-primary">Data progress</span>
        <h2 class="text-2xl sm:text-3xl font-black tracking-tight mt-1">Preparation and indexing status</h2>
        <p class="text-sm text-muted-foreground mt-1">
          Review extraction and passage indexing run as background jobs with explicit budgets and cancellation.
        </p>
      </div>
      <Button variant="outline" size="sm" class="gap-1.5" @click="load">
        <RefreshCw class="w-3.5 h-3.5" /> Refresh
      </Button>
    </div>

    <Loader2 v-if="loading" class="w-5 h-5 animate-spin text-primary mx-auto my-8" />
    <p v-else-if="error" class="text-xs text-evidence-negative font-semibold flex items-center gap-1.5" role="alert">
      <AlertTriangle class="w-3.5 h-3.5" /> {{ error }}
    </p>

    <template v-else-if="progress">
      <p v-if="progress.notice" class="text-[11px] text-muted-foreground">{{ progress.notice }}</p>

      <!-- Prepared study pointer -->
      <div v-if="demo?.configured" class="p-3.5 rounded-xl border border-evidence-verified/30 bg-evidence-verified-bg/40 text-xs flex items-center justify-between flex-wrap gap-2">
        <span class="text-evidence-verified font-bold">
          Prepared study group is {{ demo.ready ? 'ready' : 'partially prepared' }} ({{ demo.products.filter(p => p.ready).length }}/{{ demo.products.length }} products).
        </span>
        <RouterLink to="/study" class="text-primary font-bold hover:underline">Open the study →</RouterLink>
      </div>

      <!-- Coverage -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-bold">Review extraction</CardTitle>
          </CardHeader>
          <CardContent class="text-xs flex flex-col gap-1.5">
            <div class="flex justify-between font-mono text-[11px] text-muted-foreground">
              <span>{{ progress.reviews.processed }} processed</span>
              <span>{{ progress.reviews.eligible }} eligible</span>
            </div>
            <div class="h-2 rounded-full bg-muted overflow-hidden">
              <div class="h-full bg-evidence-verified" :style="{ width: percent(progress.reviews.processed, progress.reviews.eligible) + '%' }" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-bold">Passage indexing</CardTitle>
          </CardHeader>
          <CardContent class="text-xs flex flex-col gap-1.5">
            <div class="flex justify-between font-mono text-[11px] text-muted-foreground">
              <span>{{ progress.embeddings.indexed }} indexed</span>
              <span>{{ progress.embeddings.eligible }} eligible</span>
            </div>
            <div class="h-2 rounded-full bg-muted overflow-hidden">
              <div class="h-full bg-evidence-source" :style="{ width: percent(progress.embeddings.indexed, progress.embeddings.eligible) + '%' }" />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Job submission form -->
      <Card>
        <CardHeader class="pb-2 border-b">
          <CardTitle class="text-sm font-bold">Start a preparation job</CardTitle>
        </CardHeader>
        <CardContent class="pt-4 grid grid-cols-2 sm:grid-cols-5 gap-2.5 items-end text-xs">
          <label class="flex flex-col gap-1">
            <span class="font-semibold text-muted-foreground">Kind</span>
            <select v-model="form.kind" class="h-9 rounded-lg border border-input bg-background px-2 cursor-pointer">
              <option value="reviews">Analyze collected reviews</option>
              <option value="embed">Make passages searchable by meaning</option>
            </select>
          </label>
          <label class="flex flex-col gap-1">
            <span class="font-semibold text-muted-foreground">Record limit</span>
            <input v-model.number="form.limit" type="number" min="1" max="5000" class="h-9 rounded-lg border border-input bg-background px-2" />
          </label>
          <label class="flex flex-col gap-1">
            <span class="font-semibold text-muted-foreground">Product id (optional)</span>
            <input v-model="form.product_id" type="number" min="1" class="h-9 rounded-lg border border-input bg-background px-2" placeholder="all" />
          </label>
          <label class="flex flex-col gap-1">
            <span class="font-semibold text-muted-foreground">Max API attempts</span>
            <input v-model.number="form.max_calls" type="number" min="1" max="1000" class="h-9 rounded-lg border border-input bg-background px-2" />
          </label>
          <label class="flex flex-col gap-1">
            <span class="font-semibold text-muted-foreground">Time limit (s)</span>
            <input v-model.number="form.max_seconds" type="number" min="10" max="3600" class="h-9 rounded-lg border border-input bg-background px-2" />
          </label>
          <div class="col-span-2 sm:col-span-5 flex items-center justify-between flex-wrap gap-2">
            <span class="text-[11px] text-muted-foreground">
              Jobs spend the configured Gemini budget ({{ form.max_calls }} calls / {{ form.max_seconds }} s) and stop cleanly at the limit.
            </span>
            <Button size="sm" class="gap-1.5 font-bold" :disabled="submitting" @click="submitJob">
              <Loader2 v-if="submitting" class="w-3.5 h-3.5 animate-spin" />
              Queue job
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Active jobs -->
      <div v-if="activeJobs.length" class="flex flex-col gap-2">
        <h3 class="text-sm font-bold">Active jobs</h3>
        <Card v-for="job in activeJobs" :key="job.id" class="p-4">
          <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
            <div class="flex items-center gap-2">
              <Badge :variant="STATUS_VARIANT[job.status] ?? 'outline'" class="text-[10px] font-bold uppercase">{{ job.status }}</Badge>
              <span class="font-bold">{{ job.kind === 'reviews' ? 'Review analysis' : 'Passage indexing' }}</span>
              <span class="text-muted-foreground font-mono text-[11px]">
                {{ job.calls ?? 0 }}/{{ job.max_calls }} calls · {{ job.selected ?? 0 }}/{{ job.limit_count ?? '—' }} records
                <template v-if="job.product_id"> · product {{ job.product_id }}</template>
              </span>
            </div>
            <Button
              v-if="!job.cancel_requested"
              variant="outline"
              size="sm"
              class="h-7 text-[11px] gap-1 text-evidence-negative"
              @click="cancelJob(job)"
            >
              <XCircle class="w-3 h-3" /> Stop after current batch
            </Button>
            <span v-else class="text-[11px] text-evidence-unknown font-semibold">Cancellation requested — finishing the current batch</span>
          </div>
        </Card>
      </div>

      <!-- Recent terminal jobs (failed/cancelled/completed) -->
      <div v-if="finishedJobs.length" class="flex flex-col gap-2">
        <h3 class="text-sm font-bold">Recent jobs</h3>
        <Card v-for="job in finishedJobs.slice(0, 6)" :key="job.id" class="p-4">
          <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
            <div class="flex items-center gap-2">
              <Badge :variant="STATUS_VARIANT[job.status] ?? 'outline'" class="text-[10px] font-bold uppercase">{{ job.status }}</Badge>
              <span class="font-bold">{{ job.kind === 'reviews' ? 'Review analysis' : 'Passage indexing' }}</span>
              <span class="text-muted-foreground font-mono text-[11px]">
                {{ job.completed ?? 0 }}/{{ job.limit_count ?? '—' }} records · {{ job.calls ?? 0 }}/{{ job.max_calls }} calls
                <template v-if="job.product_id"> · product {{ job.product_id }}</template>
              </span>
            </div>
            <span v-if="job.error_code" class="text-[11px] text-evidence-negative font-mono">{{ job.error_code }}</span>
          </div>
        </Card>
      </div>

      <!-- Recent operations -->
      <Card>
        <CardHeader class="pb-2 border-b">
          <CardTitle class="text-sm font-bold">Recent operations</CardTitle>
        </CardHeader>
        <CardContent class="pt-3 text-[11px] font-mono flex flex-col gap-1">
          <div v-for="(op, idx) in progress.recent_operations ?? []" :key="idx" class="flex items-center justify-between gap-2 border-b border-border/30 pb-1 last:border-0">
            <span class="font-bold text-foreground">{{ op.task }}</span>
            <span class="text-muted-foreground">{{ op.status }} · {{ op.attempts }} attempt(s) · {{ Math.round(op.elapsed_ms ?? 0) }} ms</span>
          </div>
          <p v-if="(progress.recent_operations ?? []).length === 0" class="text-muted-foreground italic">No operations recorded yet.</p>
        </CardContent>
      </Card>

      <!-- Model + usage -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <Card class="p-4">
          <div class="flex items-center justify-between">
            <span class="font-bold">Model</span>
            <Badge :variant="progress.model?.enabled ? 'verified' : 'unknown'" class="text-[10px]">
              {{ progress.model?.enabled ? 'enabled' : 'disabled' }}
            </Badge>
          </div>
          <p class="font-mono text-[11px] text-muted-foreground mt-1">{{ progress.model?.model ?? '—' }}</p>
        </Card>
        <Card class="p-4">
          <span class="font-bold">Usage</span>
          <p class="font-mono text-[11px] text-muted-foreground mt-1">
            {{ progress.usage?.operations ?? 0 }} operations · {{ progress.usage?.provider_attempts ?? 0 }} provider attempts ·
            {{ progress.usage?.reported_tokens ?? 0 }} tokens · {{ progress.usage?.cache_hits ?? 0 }} cache hits
          </p>
        </Card>
      </div>
    </template>
  </div>
</template>
