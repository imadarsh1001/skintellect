<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import type { CopilotCitation, CopilotMessage, CopilotStep } from '@/lib/types'
import {
  askCopilot,
  streamCopilot,
  fetchEvidence,
  fetchCopilotSessions,
  createCopilotSession,
  fetchCopilotSession,
  deleteCopilotSession,
  fetchProduct,
} from '@/lib/api'
import { renderMarkdown } from '@/lib/markdown'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import AgentTrace from '@/components/ai/AgentTrace.vue'
import ChatMessages from '@/components/ai/ChatMessages.vue'
import PromptInput from '@/components/ai/PromptInput.vue'
import SourcesList from '@/components/ai/SourcesList.vue'
import SuggestionChip from '@/components/ai/SuggestionChip.vue'
import TaskPlan from '@/components/ai/TaskPlan.vue'
import {
  Bot,
  Check,
  ChevronRight,
  Copy,
  ExternalLink,
  MessageSquare,
  Plus,
  Quote,
  Scale,
  ShieldCheck,
  Sparkles,
  Trash2,
  User,
} from 'lucide-vue-next'

const props = defineProps({
  activeProductIds: Array as () => number[],
  personaId: String,
})

const route = useRoute()
const router = useRouter()

const emits = defineEmits(['view-details', 'toggle-compare'])

const sessionId = ref<string>('session_' + Math.random().toString(36).substring(2, 9))
const sessions = ref<any[]>([])
const queryInput = ref('')
const loading = ref(false)
const copiedMsgId = ref<string | null>(null)
const streamTick = ref(0)

async function copyMessage(id: string, text: string) {
  try {
    await navigator.clipboard.writeText(text)
    copiedMsgId.value = id
    setTimeout(() => {
      if (copiedMsgId.value === id) copiedMsgId.value = null
    }, 2000)
  } catch (e) {
    console.error('Failed to copy', e)
  }
}

const messages = ref<CopilotMessage[]>([
  {
    id: 'welcome',
    role: 'assistant',
    content:
      '👋 **Hey there! Welcome to Formulation Copilot.**\n\nI\'m your friendly cosmetic chemistry assistant—100% stable, fragrance-free, and formulated without attitude! 😄\n\nI can help you analyze INCI ingredient lists, dodge pore-clogging triggers, compare barrier repair moisturizers, and cite peer-reviewed clinical research.\n\nWhat skincare goal or formulation question can I help you conquer today? ✨',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  },
])

// Citation preview modal state
const activeCitation = ref<CopilotCitation | null>(null)
const citationEvidence = ref<any | null>(null)
const citationModalOpen = ref(false)

/** Curated starters; per-message suggestions come from structured backend
 * fields (clarification options), never from scraping the markdown. */
const samplePrompts = [
  'just exploring',
  'Compare barrier repair moisturizers with ceramides',
  'Find fungal-acne safe cleansers with no fragrance',
  'What do sensitive skin reviews report about stinging?',
  'Explain the scientific difference between glycerin and hyaluronic acid',
]

onMounted(async () => {
  await loadSessions()
  await consumeProductContext()
})

// "Ask Copilot About This Formula" hands off via ?product_id=<id>: make the
// product context visible instead of opening a generic blank session.
async function consumeProductContext() {
  const pid = Number(route.query.product_id)
  if (!pid) return
  try {
    const p = await fetchProduct(pid, props.personaId || 'uap')
    messages.value.push({
      id: 'ctx_' + Date.now(),
      role: 'assistant',
      content: `🧪 **${(p.brand ? p.brand + ' ' : '') + p.name}** is on the analysis bench — it is part of this session's product context. Ask about its INCI, your clinical fit for it, or stronger alternatives.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    })
  } catch {
    // product fetch failed; leave the session as-is
  }
  router.replace({ query: {} })
}

async function loadSessions() {
  try {
    const list = await fetchCopilotSessions()
    if (list && list.length > 0) {
      sessions.value = list
      if (!list.some((s: any) => s.session_id === sessionId.value)) {
        sessions.value.unshift({ session_id: sessionId.value, title: 'Current Session', user_turns: 0 })
      }
    } else {
      sessions.value = [{ session_id: sessionId.value, title: 'Current Session', user_turns: 0 }]
    }
  } catch {
    sessions.value = [{ session_id: sessionId.value, title: 'Current Session', user_turns: 0 }]
  }
}

function confirmDeleteSession() {
  const sid = sessionId.value
  toast('Delete this copilot session?', {
    description: 'The conversation and its stored history will be removed.',
    action: {
      label: 'Delete',
      onClick: () => void handleDeleteSession(sid),
    },
  })
}

async function handleDeleteSession(sid: string) {
  try {
    await deleteCopilotSession(sid)
  } catch {
    // never-persisted local sessions 404 here; treating them as deleted is correct
  }
  const remaining = sessions.value.filter((s: any) => s.session_id !== sid)
  if (remaining.length > 0) {
    sessions.value = remaining
    await handleSelectSession(remaining[0].session_id)
  } else {
    sessions.value = [{ session_id: sessionId.value, title: 'Current Session', user_turns: 0 }]
    await handleNewChat()
  }
  toast.success('Session deleted.')
}

async function handleNewChat() {
  try {
    const newSession = await createCopilotSession(props.personaId || 'uap')
    sessionId.value = newSession.session_id
    sessions.value = [newSession, ...sessions.value.filter(s => s.session_id !== newSession.session_id)]
    messages.value = [
      {
        id: 'welcome_' + Date.now(),
        role: 'assistant',
        content:
          '👋 **Fresh lab bench ready!** What formulation inquiry, barrier repair check, or ingredient curiosity are we exploring now? 🧪✨',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]
  } catch (err) {
    console.error('Failed to create new session', err)
    sessionId.value = 'session_' + Math.random().toString(36).substring(2, 9)
    messages.value = [
      {
        id: 'welcome_' + Date.now(),
        role: 'assistant',
        content: '👋 **Fresh lab bench ready!** What formulation inquiry or ingredient curiosity can I help you with today? 🧪✨',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]
  }
}

async function handleSelectSession(sid: string) {
  if (!sid) return
  sessionId.value = sid
  try {
    const s = await fetchCopilotSession(sid)
    if (s && s.messages && s.messages.length > 0) {
      messages.value = s.messages.map((m: any, idx: number) => ({
        id: `sess_msg_${idx}_${Date.now()}`,
        role: m.role,
        content: m.content,
        timestamp: m.timestamp ? new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
      }))
    } else {
      messages.value = [
        {
          id: 'welcome_' + Date.now(),
          role: 'assistant',
          content: 'Session restored. How can I help you today?',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]
    }
  } catch (err) {
    console.error('Failed to switch session', err)
  }
}

function submitCustomClarification(msg: CopilotMessage) {
  const text = msg.customClarificationText?.trim()
  if (!text) return
  msg.showCustomClarification = false
  handleSend(text)
}

async function handleSend(promptText?: string) {
  const query = promptText || queryInput.value.trim()
  if (!query || loading.value) return

  queryInput.value = ''

  // User message
  messages.value.push({
    id: 'user_' + Date.now(),
    role: 'user',
    content: query,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  })

  loading.value = true

  // Assistant placeholder: no client-side intent guessing. The real task plan
  // arrives from the backend stream (node_update carries the todo_list).
  const tempMsgId = 'assistant_' + Date.now()
  messages.value.push({
    id: tempMsgId,
    role: 'assistant',
    content: '',
    todo_list: [{ task: 'Interpreting your formulation question', status: 'in_progress' as const }],
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  })

  try {
    await streamCopilot(
      {
        session_id: sessionId.value,
        persona_id: props.personaId || 'uap',
        query,
        product_ids: props.activeProductIds && props.activeProductIds.length > 0 ? props.activeProductIds : undefined,
      },
      (event) => {
        const target = messages.value.find(m => m.id === tempMsgId)
        if (!target) return
        streamTick.value++

        if (event.event === 'stream_fallback') {
          // Degraded mode is observable (D1): tell the user streaming is off.
          toast.info('Live streaming is unavailable right now — answering without it.')
          return
        }

        if (event.event === 'node_update') {
          // Workflow steps come from the backend workflow events only.
          if (event.node === 'interpret_intent') {
            target.streamingStage = 'Interpreting cosmetic intent & planning agent workflow...'
            if (event.data?.todo_list && event.data.todo_list.length > 0) {
              target.todo_list = event.data.todo_list.map((t: any, idx: number) => ({
                task: t.task,
                status: idx === 0 ? 'in_progress' : 'pending',
              }))
            }
          } else if (event.node === 'retrieve_candidates') {
            target.streamingStage = 'Searching catalog across verified INCI profiles...'
          } else if (event.node === 'plan_and_retrieve_evidence') {
            target.streamingStage = 'Extracting review sentiments & scientific references...'
          } else if (event.node === 'synthesize_grounded_answer') {
            target.streamingStage = 'Synthesizing evidence-backed response...'
          }
          if (event.node) markCompletedSteps(target.todo_list ?? [], event.node)
        } else if (event.event === 'final_result') {
          const res = event.data
          if (res.session_title) {
            const current = sessions.value.find(s => s.session_id === sessionId.value)
            if (current) {
              current.title = res.session_title
              current.user_turns = (current.user_turns || 0) + 1
            } else {
              sessions.value.unshift({ session_id: sessionId.value, title: res.session_title, user_turns: 1 })
            }
          }

          target.content = res.answer || res.content || 'Completed analysis based on verified catalog data.'
          target.todo_list = (res.todo_list && res.todo_list.length > 0)
            ? res.todo_list.map((t: any) => ({ ...t, status: 'completed' }))
            : (target.todo_list ?? []).map(t => ({ ...t, status: 'completed' }))
          target.matching_products = res.search?.products || []
          target.total_matches = res.search?.total || (target.matching_products ? target.matching_products.length : 0)
          target.review_insights = res.review_insights || []
          target.alternatives = res.alternatives || []
          target.tool_calls = (res.trace?.tools || []).map((t: string) => ({
            name: t,
            args: {},
            status: 'done',
          }))
          target.citations = (res.references || res.citations || []).map((c: any) => ({
            id: c.evidence_id || c.id || String(c),
            title: c.title || c.evidence_id || 'Reference Citation',
            quote: c.summary || c.quote || c.text,
            url: c.url,
            source_kind: 'reference_note',
          }))
          target.trace = res.trace
          target.clarification = res.clarification
          target.showCustomClarification = false
          target.customClarificationText = ''
          target.streamingStage = undefined
        }
      },
    )
  } catch (err: any) {
    const target = messages.value.find(m => m.id === tempMsgId)
    if (target) {
      target.content = `I encountered an issue querying the catalog: ${err.message || 'Service temporarily unavailable'}.`
      target.todo_list = target.todo_list?.map(s => ({ ...s, status: 'failed' as const }))
    }
  } finally {
    loading.value = false
    streamTick.value++
  }
}

/** Steps completed by the time a later stream node fires. The backend is
 * the source of truth for node order; this only marks prior steps done. */
const NODE_ORDER = ['interpret_intent', 'retrieve_candidates', 'plan_and_retrieve_evidence', 'synthesize_grounded_answer']
function markCompletedSteps(steps: CopilotStep[], node: string) {
  const reached = NODE_ORDER.indexOf(node)
  if (reached <= 0 || steps.length === 0) return
  steps.forEach((step, idx) => {
    if (idx < Math.min(reached, steps.length - 1) && step.status === 'pending') {
      step.status = 'completed'
    }
    if (idx === Math.min(reached, steps.length - 1)) {
      step.status = 'in_progress'
    }
  })
}

async function inspectCitation(cit: CopilotCitation) {
  activeCitation.value = cit
  citationEvidence.value = null
  citationModalOpen.value = true

  try {
    const data = await fetchEvidence(cit.id)
    citationEvidence.value = data
  } catch {
    citationEvidence.value = { quote: cit.quote || 'Source excerpt verification unavailable offline.' }
  }
}

const lastAssistantContent = computed(() => {
  const last = messages.value[messages.value.length - 1]
  return `${last?.id ?? ''}:${(last?.content ?? '').length}:${(last?.todo_list ?? []).map(s => s.status).join('')}`
})
</script>

<template>
  <div class="flex flex-col h-[750px] rounded-2xl border bg-card shadow-xs overflow-hidden">
    <!-- Header with Session Switcher and New Chat -->
    <div class="flex items-center justify-between p-4 border-b bg-muted/30">
      <div class="flex items-center gap-3">
        <div class="p-2.5 rounded-xl bg-primary/10 text-primary">
          <Sparkles class="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 class="font-bold text-sm text-foreground flex items-center gap-2">
            Formulation Research Copilot
            <Badge variant="verified" class="text-[10px] py-0 px-1.5 font-bold">Deep Agents</Badge>
            <Badge variant="source" class="text-[10px] py-0 px-1.5 font-bold">LangGraph</Badge>
          </h3>
          <p class="text-[11px] text-muted-foreground">
            Multi-domain formulation reasoning with verbatim quotation enforcement and task decomposition.
          </p>
        </div>
      </div>

      <!-- Session Switcher & New Chat Button -->
      <div class="flex items-center gap-2">
        <div v-if="sessions.length > 1">
          <Select :model-value="sessionId" @update:model-value="(val) => handleSelectSession(String(val))">
            <SelectTrigger class="h-8 text-xs max-w-[170px] truncate shadow-2xs">
              <SelectValue placeholder="Select session" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="s in sessions" :key="s.session_id" :value="s.session_id" class="text-xs">
                {{ s.title }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button
          variant="outline"
          size="sm"
          class="h-8 px-2.5 text-xs font-semibold gap-1.5 cursor-pointer text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors shadow-2xs"
          title="Delete current session"
          @click="confirmDeleteSession()"
        >
          <Trash2 class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">Delete</span>
        </Button>
        <Button
          variant="outline"
          size="sm"
          class="h-8 px-2.5 text-xs font-semibold gap-1.5 cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors shadow-2xs"
          @click="handleNewChat()"
          title="Start fresh session"
        >
          <Plus class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">New Chat</span>
        </Button>
      </div>
    </div>

    <!-- Messages Container (Message Scroller keeps the stream pinned) -->
    <ChatMessages :stream-tick="streamTick">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="flex gap-3 max-w-4xl"
        :class="msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''"
      >
        <!-- Avatar -->
        <div
          class="size-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold shadow-xs"
          :class="msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted text-foreground border'"
        >
          <User v-if="msg.role === 'user'" class="w-4 h-4" />
          <Bot v-else class="w-4 h-4 text-primary" />
        </div>

        <!-- Bubble -->
        <div class="flex flex-col gap-2 max-w-[90%] sm:max-w-[85%]">
          <div
            class="p-4 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-2xs relative group/bubble"
            :class="msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted/40 border text-foreground'"
          >
            <!-- Header bar: identity, live stage, copy -->
            <div v-if="msg.role === 'assistant'" class="flex items-center justify-between mb-2 pb-1.5 border-b border-border/30">
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
                  <Sparkles class="w-3 h-3 text-primary" />
                  Formulation Copilot
                </span>
                <span
                  v-if="loading && msg.streamingStage && msg.id === messages[messages.length - 1]?.id"
                  class="inline-flex items-center gap-1 text-[10px] font-medium text-primary animate-pulse"
                >
                  {{ msg.streamingStage }}
                </span>
              </div>
              <button
                type="button"
                @click="copyMessage(msg.id, msg.content)"
                class="opacity-60 hover:opacity-100 p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-all cursor-pointer"
                :title="copiedMsgId === msg.id ? 'Copied!' : 'Copy response'"
              >
                <Check v-if="copiedMsgId === msg.id" class="w-3.5 h-3.5 text-emerald-600" />
                <Copy v-else class="w-3.5 h-3.5" />
              </button>
            </div>

            <!-- Workflow plan (Plan/Task pattern) -->
            <TaskPlan
              v-if="msg.role === 'assistant' && msg.todo_list && msg.todo_list.length > 0"
              :steps="msg.todo_list"
              :live="loading && msg.id === messages[messages.length - 1]?.id"
            />

            <!-- Narrative Message Text (sanitized markdown) -->
            <div v-if="msg.content" class="prose-copilot leading-relaxed" v-html="renderMarkdown(msg.content)" />

            <!-- Interactive Suggestion Chips (structured backend fields only) -->
            <div
              v-if="msg.clarification && msg.clarification.options && msg.clarification.options.length > 0"
              class="mt-4 pt-3.5 border-t border-border/60 space-y-2.5"
            >
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
                  <Sparkles class="w-3.5 h-3.5 text-primary" />
                  Select Formulation Focus (HITL)
                </span>
                <span class="text-[10px] text-muted-foreground">
                  Click to explore or customize below
                </span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  v-for="(opt, oIdx) in msg.clarification.options"
                  :key="opt.id || oIdx"
                  type="button"
                  class="p-2.5 rounded-xl border border-primary/20 bg-primary/5 hover:bg-primary/10 hover:border-primary/50 text-left transition-all cursor-pointer shadow-2xs group flex flex-col justify-between gap-1"
                  @click="handleSend(opt.query)"
                >
                  <div class="flex items-center justify-between gap-1">
                    <span class="text-xs font-bold text-foreground group-hover:text-primary transition-colors flex items-center gap-1.5">
                      <span class="inline-flex items-center justify-center w-4 h-4 rounded-full bg-primary/20 text-primary text-[10px] font-bold">
                        {{ String.fromCharCode(65 + oIdx) }}
                      </span>
                      {{ opt.title }}
                    </span>
                    <ChevronRight class="w-3.5 h-3.5 text-primary opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all shrink-0" />
                  </div>
                  <p class="text-[11px] text-muted-foreground leading-snug line-clamp-2">
                    {{ opt.description }}
                  </p>
                </button>
              </div>

              <!-- Custom Option Toggle & Input -->
              <div v-if="msg.clarification.allow_custom" class="mt-2 pt-2 border-t border-border/30">
                <div v-if="!msg.showCustomClarification">
                  <button
                    type="button"
                    class="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors cursor-pointer py-1 px-2 rounded-lg hover:bg-muted/40"
                    @click="msg.showCustomClarification = true"
                  >
                    <Plus class="w-3.5 h-3.5 text-primary" />
                    <span>Other: Specify custom constraint or ingredients...</span>
                  </button>
                </div>
                <div v-else class="flex items-center gap-2 mt-1">
                  <input
                    v-model="msg.customClarificationText"
                    placeholder="e.g. Under $25, fungal-acne safe with no niacinamide"
                    class="h-8 text-xs flex-grow rounded-lg border border-input bg-background px-3 focus:outline-none focus:ring-1 focus:ring-primary"
                    @keydown.enter="submitCustomClarification(msg)"
                  />
                  <Button
                    size="sm"
                    class="h-8 px-3 text-xs"
                    :disabled="!msg.customClarificationText?.trim()"
                    @click="submitCustomClarification(msg)"
                  >
                    Submit Focus
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    class="h-8 px-2 text-xs text-muted-foreground"
                    @click="msg.showCustomClarification = false"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>

            <!-- Matching Formulations Cards -->
            <div
              v-if="msg.matching_products && msg.matching_products.length > 0"
              class="mt-4 pt-3.5 border-t border-border/60 space-y-2.5"
            >
              <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <ShieldCheck class="w-3.5 h-3.5 text-emerald-600" />
                Matching Formulations (Top {{ Math.min(msg.matching_products.length, 4) }} of {{ msg.total_matches || msg.matching_products.length }})
              </span>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <div
                  v-for="p in msg.matching_products.slice(0, 4)"
                  :key="p.id"
                  class="p-3 rounded-xl border bg-card/90 hover:border-primary/50 transition-all flex flex-col justify-between gap-2 shadow-2xs"
                >
                  <div>
                    <div class="flex items-start justify-between gap-1.5">
                      <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground truncate">{{ p.brand }}</span>
                      <span class="text-xs font-bold text-foreground">{{ p.price_tier || '$$' }}</span>
                    </div>
                    <h5 class="font-bold text-xs text-foreground line-clamp-1 mt-0.5">{{ p.name }}</h5>
                    <div class="flex items-center gap-1 mt-1.5 flex-wrap">
                      <Badge v-if="p.formula_status === 'verified_complete'" variant="verified" class="text-[9px] py-0 px-1 font-bold">
                        Verified INCI
                      </Badge>
                      <Badge v-else variant="unknown" class="text-[9px] py-0 px-1 font-bold">Unverified</Badge>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 pt-1.5 border-t border-border/40 text-[11px]">
                    <button
                      class="font-bold text-primary hover:underline flex items-center gap-1 cursor-pointer"
                      @click="emits('view-details', p)"
                    >
                      <ExternalLink class="w-3 h-3" /> View Dossier
                    </button>
                    <span class="text-muted-foreground text-[10px]">·</span>
                    <button
                      class="font-semibold text-muted-foreground hover:text-foreground cursor-pointer"
                      @click="emits('toggle-compare', p)"
                    >
                      + Compare
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Review Aspect Observations -->
            <div
              v-if="msg.review_insights && msg.review_insights.length > 0"
              class="mt-4 pt-3.5 border-t border-border/60 space-y-2"
            >
              <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <MessageSquare class="w-3.5 h-3.5 text-purple-600" />
                Reported Review Experiences & Aspect Observations
              </span>
              <div class="space-y-1.5">
                <template v-for="(revGroup, rIdx) in msg.review_insights" :key="rIdx">
                  <div
                    v-for="(obs, oIdx) in (revGroup.observations || []).filter((o: any) => o.span || o.quote || o.text).slice(0, 3)"
                    :key="oIdx"
                    class="p-2.5 rounded-xl border bg-background/80 text-xs flex flex-col gap-1 shadow-2xs"
                  >
                    <div class="flex items-center justify-between gap-2">
                      <span class="font-bold text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-muted text-foreground">
                        {{ obs.aspect || 'Texture' }}
                      </span>
                      <span
                        class="text-[10px] font-bold px-1.5 py-0.2 rounded"
                        :class="obs.sentiment === 'negative' ? 'bg-rose-100 text-rose-800' : obs.sentiment === 'positive' ? 'bg-emerald-100 text-emerald-800' : 'bg-purple-100 text-purple-800'"
                      >
                        {{ obs.sentiment || 'observed' }}
                      </span>
                    </div>
                    <p class="italic text-foreground/90 font-serif text-[11px] leading-relaxed">
                      "{{ obs.span || obs.quote || obs.text }}"
                    </p>
                  </div>
                </template>
              </div>
            </div>

            <!-- Formula Alternatives / Dupes -->
            <div
              v-if="msg.alternatives && msg.alternatives.length > 0"
              class="mt-4 pt-3.5 border-t border-border/60 space-y-2"
            >
              <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Scale class="w-3.5 h-3.5 text-blue-600" />
                Formula Alternatives & Shared Ingredients
              </span>
              <div class="space-y-2">
                <template v-for="(altGroup, aIdx) in msg.alternatives" :key="aIdx">
                  <div
                    v-for="alt in (altGroup.alternatives || []).slice(0, 2)"
                    :key="alt.id"
                    class="p-2.5 rounded-xl border bg-background/80 text-xs space-y-1 shadow-2xs"
                  >
                    <div class="flex items-center justify-between font-bold">
                      <span>{{ alt.brand }} - {{ alt.name }}</span>
                      <span class="text-primary font-mono text-[11px]">{{ alt.similarity ? alt.similarity + '%' : '' }}</span>
                    </div>
                    <p class="text-[11px] text-muted-foreground">
                      <strong class="text-foreground">Shared:</strong> {{ alt.shared_ingredients?.slice(0, 4).join(', ') }}
                    </p>
                  </div>
                </template>
              </div>
            </div>

            <!-- Sources (AI Elements Sources pattern) -->
            <SourcesList
              v-if="msg.role === 'assistant'"
              :citations="msg.citations || []"
              @inspect="inspectCitation"
            />

            <!-- Agent Trace (AI Elements Trace pattern) -->
            <AgentTrace v-if="msg.role === 'assistant' && msg.trace" :trace="msg.trace" v-model:open="msg.showDebugger" />
          </div>
          <span class="text-[10px] text-muted-foreground px-1" :class="msg.role === 'user' ? 'text-right' : ''">
            {{ msg.timestamp }}
          </span>
        </div>
      </div>
    </ChatMessages>

    <!-- Starter Suggestions (structured, only on a fresh conversation) -->
    <div v-if="messages.length <= 2" class="p-3 border-t bg-muted/20 flex items-center gap-2 overflow-x-auto">
      <span class="text-[11px] font-bold text-muted-foreground shrink-0">Try asking:</span>
      <div class="flex items-center gap-1.5">
        <SuggestionChip
          v-for="prompt in samplePrompts"
          :key="prompt"
          :suggestion="prompt"
          :disabled="loading"
          @select="handleSend"
        />
      </div>
    </div>

    <!-- Input Footer (AI Elements Prompt Input pattern) -->
    <PromptInput
      v-model="queryInput"
      :busy="loading"
      placeholder="Ask anything about cosmetic chemistry, barrier repair, skin sensitivity, reviews..."
      @submit="handleSend()"
    />

    <!-- Verbatim Citation Modal -->
    <Dialog :open="citationModalOpen" @update:open="(val: boolean) => citationModalOpen = val">
      <DialogContent class="max-w-lg rounded-2xl">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2 text-base font-bold">
            <Quote class="w-4 h-4 text-primary" />
            Verbatim Evidence Source
          </DialogTitle>
          <DialogDescription>
            Exact excerpt referenced in reasoning without editorial alteration.
          </DialogDescription>
        </DialogHeader>

        <div class="flex flex-col gap-3 py-3 text-xs">
          <div class="p-3 rounded-xl border bg-muted/40 font-mono text-xs leading-relaxed text-foreground">
            {{ citationEvidence?.quote || activeCitation?.quote || 'Loading excerpt from secure corpus...' }}
          </div>

          <div v-if="activeCitation?.url" class="flex items-center justify-between text-xs pt-2">
            <span class="text-muted-foreground font-semibold">Source URL:</span>
            <a
              :href="activeCitation.url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-primary flex items-center gap-1 hover:underline font-bold"
            >
              {{ activeCitation.url.replace(/^https?:\/\//, '').split('/')[0] }}
              <ExternalLink class="w-3 h-3" />
            </a>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>
