<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CopilotMessage, CopilotCitation, Product } from '@/lib/types'
import {
  askCopilot,
  streamCopilot,
  fetchEvidence,
  fetchCopilotSessions,
  createCopilotSession,
  fetchCopilotSession,
  deleteCopilotSession,
} from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import { marked } from 'marked'

marked.setOptions({
  gfm: true,
  breaks: true,
})

function renderMarkdown(content?: string): string {
  if (!content) return ''
  try {
    return marked.parse(content) as string
  } catch {
    return content
  }
}

function getSuggestions(content?: string, role?: string): string[] {
  if (!content) return []
  const results: string[] = []
  // Matches prompt examples formatted like *"Find ... "* or "Compare ... "
  const regex = /(?:Try\s+)?[\*"]+([A-Z][^\n\*\"]{8,95}\??)[\*"]+/g
  let match
  while ((match = regex.exec(content)) !== null) {
    const text = match[1].trim()
    if (
      !results.includes(text) &&
      !text.startsWith('http') &&
      !text.includes('|') &&
      !text.includes('·') &&
      (text.startsWith('Find') ||
       text.startsWith('Compare') ||
       text.startsWith('Explain') ||
       text.startsWith('What') ||
       text.startsWith('How') ||
       text.startsWith('Show') ||
       text.startsWith('Lightweight') ||
       text.startsWith('just exploring'))
    ) {
      results.push(text)
    }
  }
  if (results.length === 0 && role === 'assistant') {
    const cLower = content.toLowerCase()
    if (cLower.includes('ceramide') || cLower.includes('barrier')) {
      return [
        'Compare barrier repair moisturizers with ceramides',
        'What do sensitive skin reviews report about stinging?',
        'Explain the scientific difference between glycerin and hyaluronic acid',
      ]
    }
    if (cLower.includes('cleanser') || cLower.includes('fungal')) {
      return [
        'Find fungal-acne safe cleansers with no fragrance',
        'Lightweight moisturizer for oily skin',
        'Compare barrier repair moisturizers with ceramides',
      ]
    }
    return [
      'Compare barrier repair moisturizers with ceramides',
      'Find fungal-acne safe cleansers with no fragrance',
      'Explain the scientific difference between glycerin and hyaluronic acid',
      'What do sensitive skin reviews report about stinging?',
    ]
  }
  return results.slice(0, 4)
}
import {
  Sparkles,
  Send,
  Loader2,
  CheckCircle2,
  Circle,
  Clock,
  BookOpen,
  Quote,
  ExternalLink,
  Bot,
  User,
  ShieldCheck,
  MessageSquare,
  Scale,
  FlaskConical,
  Star,
  ChevronRight,
  Plus,
  Trash2,
  Zap,
  Activity,
  Layers,
  ChevronDown,
  Copy,
  Check,
} from 'lucide-vue-next'

const props = defineProps({
  activeProductIds: Array as () => number[],
  personaId: String,
})

const emits = defineEmits(['view-details', 'toggle-compare'])

const sessionId = ref<string>('session_' + Math.random().toString(36).substring(2, 9))
const sessions = ref<any[]>([])
const queryInput = ref('')
const loading = ref(false)
const copiedMsgId = ref<string | null>(null)

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

const samplePrompts = [
  'just exploring',
  'Compare barrier repair moisturizers with ceramides',
  'Find fungal-acne safe cleansers with no fragrance',
  'What do sensitive skin reviews report about stinging?',
  'Explain the scientific difference between glycerin and hyaluronic acid',
]

onMounted(async () => {
  await loadSessions()
})

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

function isAgentActive(trace: any, agentName: string): boolean {
  if (!trace || !trace.activated_agents) return false
  return trace.activated_agents.includes(agentName)
}

function formatEventTime(isoString?: string): string {
  if (!isoString) return ''
  try {
    const d = new Date(isoString)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return isoString
  }
}

function submitCustomClarification(msg: any) {
  const text = msg.customClarificationText?.trim()
  if (!text) return
  msg.showCustomClarification = false
  handleSend(text)
}

async function handleSend(promptText?: string) {
  const query = promptText || queryInput.value.trim()
  if (!query || loading.value) return

  queryInput.value = ''

  // Add User Message
  messages.value.push({
    id: 'user_' + Date.now(),
    role: 'user',
    content: query,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  })

  loading.value = true

  // Temporary Assistant placeholder
  const tempMsgId = 'assistant_' + Date.now()
  const qLower = query.trim().toLowerCase()
  const isGreeting = /^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|who\s+are\s+you|help)[\s!.?]*$/.test(qLower)
  const isExplore = /(just exploring|exploring|explore|browse|looking around|show me products|popular products|top rated)/.test(qLower)
  const isCompare = /\b(compare|versus|vs\.?)\b/.test(qLower)
  const isScience = /\b(explain|difference\s+between|what\s+is|what\s+are|how\s+does|why\s+.*(bad|good|harmful)|sulphate|sulfate|sle|sles|sls|surfactant)\b/i.test(qLower)
  const isChat = /^(are\s+you|why\s+(did|didn|can|cant)|double\s+check|do\s+you\s+know|tell\s+me|joke|make\s+me\s+laugh)/i.test(qLower)

  const initialTasks = (isGreeting || isChat)
    ? [{ task: isGreeting ? 'Acknowledge greeting & present copilot capabilities' : 'Formulate conversational response', status: 'in_progress' as const }]
    : isExplore
    ? [
        { task: 'Identify exploration intent & catalog scope', status: 'in_progress' as const },
        { task: 'Retrieve standout verified formulations across routine steps', status: 'pending' as const },
        { task: 'Synthesize curated catalog showcase with suggestions', status: 'pending' as const },
      ]
    : isCompare
    ? [
        { task: 'Identify target active lipids & formula category', status: 'in_progress' as const },
        { task: 'Retrieve top eligible formulations for comparative analysis', status: 'pending' as const },
        { task: 'Extract review sentiments & key active differences', status: 'pending' as const },
        { task: 'Synthesize side-by-side comparison across skin types & budgets', status: 'pending' as const },
      ]
    : isScience
    ? [
        { task: 'Parse cosmetic chemistry topics & active ingredients', status: 'in_progress' as const },
        { task: 'Retrieve scientific monographs & clinical references', status: 'pending' as const },
        { task: 'Synthesize evidence-backed formulation explanation', status: 'pending' as const },
      ]
    : [
        { task: 'Interpret cosmetic intent & active constraints', status: 'in_progress' as const },
        { task: 'Retrieve matching formulations across catalog', status: 'pending' as const },
        { task: 'Extract aspect reviews & scientific monographs', status: 'pending' as const },
        { task: 'Synthesize grounded evidence-backed response', status: 'pending' as const },
      ]

  messages.value.push({
    id: tempMsgId,
    role: 'assistant',
    content: isGreeting
      ? 'Greeting formulation copilot...'
      : isChat
      ? 'Consulting formulation copilot...'
      : isExplore
      ? 'Curating top verified formulations across catalog steps...'
      : isCompare
      ? 'Comparing formulation profiles and active ingredients...'
      : isScience
      ? 'Synthesizing cosmetic chemistry and ingredient evidence...'
      : 'Decomposing formulation inquiry and consulting scientific catalog...',
    todo_list: initialTasks,
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

        if (event.event === 'node_update') {
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
            if (target.todo_list && target.todo_list.length > 1) {
              target.todo_list[0].status = 'completed'
              target.todo_list[1].status = 'in_progress'
            }
          } else if (event.node === 'plan_and_retrieve_evidence') {
            target.streamingStage = 'Extracting review sentiments & scientific references...'
            if (target.todo_list && target.todo_list.length > 2) {
              target.todo_list[1].status = 'completed'
              target.todo_list[2].status = 'in_progress'
            }
          } else if (event.node === 'synthesize_grounded_answer') {
            target.streamingStage = 'Synthesizing evidence-backed response...'
            if (target.todo_list) {
              target.todo_list.forEach((t, i) => {
                if (i < target.todo_list!.length - 1) t.status = 'completed'
                else t.status = 'in_progress'
              })
            }
          }
        } else if (event.event === 'final_result') {
          const res = event.data
          // Update session title in session selector if returned
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
            : (target.todo_list || initialTasks).map(t => ({ ...t, status: 'completed' }))
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
          target.showDebugger = false
          target.showPlan = false // Hidden by default; opens only on click
          target.streamingStage = undefined
        }
      }
    )
  } catch (err: any) {
    const target = messages.value.find(m => m.id === tempMsgId)
    if (target) {
      target.content = `I encountered an issue querying the catalog: ${err.message || 'Service temporarily unavailable'}.`
      target.todo_list = target.todo_list?.map(s => ({ ...s, status: 'failed' }))
    }
  } finally {
    loading.value = false
  }
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
        <div v-if="sessions.length > 1" class="relative">
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
          class="h-8 px-2.5 text-xs font-semibold gap-1.5 cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors shadow-2xs"
          @click="handleNewChat()"
          title="Start fresh session"
        >
          <Plus class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">New Chat</span>
        </Button>
      </div>
    </div>

    <!-- Messages Container -->
    <div class="flex-grow overflow-y-auto p-4 sm:p-5 flex flex-col gap-5">
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
            <!-- Header bar for bubble: copy button & live streaming indicator -->
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
                  <Loader2 class="w-2.5 h-2.5 animate-spin" />
                  {{ msg.streamingStage }}
                </span>
              </div>
              <div class="flex items-center gap-1">
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
            </div>

            <!-- Agent Task Planning Checklist (Deep Agents todo_list) - Collapsible on click -->
            <div
              v-if="msg.todo_list && msg.todo_list.length > 1"
              class="mb-3"
            >
              <button
                type="button"
                @click="msg.showPlan = !msg.showPlan"
                class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-background/80 hover:bg-background border border-border/60 text-muted-foreground hover:text-foreground transition-all cursor-pointer shadow-2xs group"
                :title="msg.showPlan ? 'Click to hide underlying thinking' : 'Click to inspect underlying thinking & agent task plan'"
              >
                <Clock class="w-3 h-3 text-primary group-hover:rotate-45 transition-transform" />
                <span>{{ msg.showPlan ? 'Hide underlying thinking' : 'Execution Plan (' + msg.todo_list.length + ' steps)' }}</span>
                <ChevronDown class="w-3 h-3 text-muted-foreground transition-transform duration-200" :class="{ 'rotate-180': msg.showPlan }" />
              </button>

              <div
                v-if="msg.showPlan"
                class="mt-2 p-3 rounded-xl bg-background/95 border text-xs space-y-1.5 shadow-2xs"
              >
                <div class="font-bold text-muted-foreground uppercase text-[10px] tracking-wider mb-1 flex items-center justify-between">
                  <span class="flex items-center gap-1.5">
                    <Clock class="w-3.5 h-3.5 text-primary" />
                    Deep Agents Task Decomposition
                  </span>
                  <span class="text-[10px] font-normal text-muted-foreground">
                    {{ msg.todo_list.filter((s: any) => s.status === 'completed').length }} / {{ msg.todo_list.length }} steps done
                  </span>
                </div>
                <div
                  v-for="(step, sIdx) in msg.todo_list"
                  :key="sIdx"
                  class="flex items-center gap-2 text-xs"
                >
                  <CheckCircle2 v-if="step.status === 'completed'" class="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <Loader2 v-else-if="step.status === 'in_progress'" class="w-3.5 h-3.5 animate-spin text-primary shrink-0" />
                  <Circle v-else class="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                  <span :class="step.status === 'completed' ? 'text-foreground font-medium' : 'text-muted-foreground'">
                    {{ step.task }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Narrative Message Text -->
            <div class="prose-copilot leading-relaxed" v-html="renderMarkdown(msg.content)" />

            <!-- Interactive Suggestion Chips (Quick Prompts) -->
            <div
              v-if="msg.role === 'assistant' && getSuggestions(msg.content, msg.role).length > 0"
              class="mt-3 flex flex-wrap gap-1.5 pt-2.5 border-t border-border/40"
            >
              <button
                v-for="(sug, sIdx) in getSuggestions(msg.content, msg.role)"
                :key="sIdx"
                type="button"
                class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-primary/10 text-primary hover:bg-primary/20 border border-primary/25 transition-all cursor-pointer shadow-2xs hover:scale-[1.02]"
                @click="handleSend(sug)"
              >
                <Sparkles class="w-3 h-3 text-primary shrink-0" />
                <span>{{ sug }}</span>
              </button>
            </div>

            <!-- Interactive HITL Clarification Cards & Custom Option -->
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

              <!-- Option Cards Grid -->
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

              <!-- Blank / Custom Option Toggle & Input -->
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
                  <Input
                    v-model="msg.customClarificationText"
                    placeholder="e.g. Under $25, fungal-acne safe with no niacinamide"
                    class="h-8 text-xs flex-grow"
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

            <!-- 1. Matching Formulations Cards (if any) -->
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
                      <span v-for="(c, cIdx) in p.checks || []" :key="cIdx" class="text-[10px] text-muted-foreground">
                        <span v-if="c.matched_names && c.matched_names.length" class="text-primary font-semibold">
                          {{ c.matched_names.slice(0, 2).join(', ') }}
                        </span>
                      </span>
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

            <!-- 2. Review Aspect Observations (if any) -->
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

            <!-- 3. Formula Alternatives / Dupes (if any) -->
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

            <!-- 4. Scientific Literature Citations -->
            <div v-if="msg.citations && msg.citations.length > 0" class="mt-4 pt-3 border-t border-border/60">
              <span class="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block mb-1.5">
                Scientific & Catalog Evidence
              </span>
              <div class="flex flex-wrap gap-1.5">
                <Badge
                  v-for="cit in msg.citations"
                  :key="cit.id"
                  variant="source"
                  class="cursor-pointer text-[11px] gap-1 hover:bg-blue-100 transition-colors font-semibold"
                  @click="inspectCitation(cit)"
                >
                  <BookOpen class="w-3 h-3" />
                  {{ cit.title }}
                </Badge>
              </div>
            </div>

            <!-- 5. Agent Trace & Debugger Drawer -->
            <Collapsible v-if="msg.trace" v-model:open="msg.showDebugger" class="mt-4 pt-3.5 border-t border-border/60">
              <CollapsibleTrigger as-child>
                <button
                  type="button"
                  class="w-full flex items-center justify-between p-2 rounded-xl bg-background/90 hover:bg-background border border-border/70 transition-colors text-left text-xs cursor-pointer group shadow-2xs"
                >
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="flex items-center gap-1 font-bold text-amber-600 dark:text-amber-400">
                      <Zap class="w-3.5 h-3.5 fill-current" />
                      Agent Trace & Debugger
                    </span>
                    <Badge variant="outline" class="text-[10px] py-0 px-1.5 uppercase font-mono font-bold bg-muted/50 border-border/80">
                      Route: {{ msg.trace.intent_route || 'auto' }}
                    </Badge>
                    <Badge
                      :variant="((msg.trace.activated_agents || []).length <= 2) ? 'verified' : 'source'"
                      class="text-[10px] py-0 px-1.5 font-bold"
                    >
                      {{ (msg.trace.activated_agents || []).length }} Active · {{ (msg.trace.bypassed_agents || []).length }} Bypassed
                    </Badge>
                    <span v-if="msg.trace.elapsed_ms" class="text-[10px] text-muted-foreground font-mono">
                      {{ msg.trace.elapsed_ms }}ms
                    </span>
                  </div>
                  <div class="flex items-center gap-1 text-muted-foreground group-hover:text-foreground">
                    <span class="text-[10px] font-semibold">{{ msg.showDebugger ? 'Hide' : 'Inspect' }}</span>
                    <ChevronDown
                      class="w-3.5 h-3.5 transition-transform duration-200"
                      :class="msg.showDebugger ? 'rotate-180' : ''"
                    />
                  </div>
                </button>
              </CollapsibleTrigger>

              <!-- Expanded Debugger Drawer -->
              <CollapsibleContent>
                <div
                  class="mt-2.5 p-3 rounded-xl border bg-card/95 text-xs flex flex-col gap-3 font-sans shadow-xs"
                >
                  <!-- Section 1: Intent Routing Decision -->
                  <div class="space-y-1">
                    <div class="flex items-center justify-between text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
                      <span class="flex items-center gap-1">
                        <Activity class="w-3 h-3 text-primary" />
                        Intent Router Decision
                      </span>
                      <span class="font-mono text-[10px] lowercase text-primary font-bold">{{ msg.trace.intent_route }}</span>
                    </div>
                    <p class="text-[11px] text-foreground bg-muted/40 p-2.5 rounded-lg border border-border/50 font-mono leading-relaxed">
                      {{ msg.trace.route_reason || 'Route dynamically mapped from query intent patterns.' }}
                    </p>
                  </div>

                  <!-- Section 2: Dynamic Agent Dispatch Matrix -->
                  <div class="space-y-1.5">
                    <div class="text-[11px] font-bold text-muted-foreground uppercase tracking-wider flex items-center justify-between">
                      <span class="flex items-center gap-1">
                        <Layers class="w-3 h-3 text-indigo-500" />
                        Agent Dispatch Matrix
                      </span>
                      <span class="text-[10px] font-normal text-muted-foreground">
                        {{ msg.trace.agents_summary || 'Selective tool activation' }}
                      </span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <!-- Catalog Search -->
                      <div
                        class="p-2 rounded-lg border flex items-center justify-between text-[11px]"
                        :class="isAgentActive(msg.trace, 'search_catalog') ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-950 dark:text-emerald-100 font-medium' : 'bg-muted/30 border-dashed border-border/60 text-muted-foreground'"
                      >
                        <span>1. Catalog Search</span>
                        <Badge
                          :variant="isAgentActive(msg.trace, 'search_catalog') ? 'verified' : 'outline'"
                          class="text-[9px] py-0 px-1 font-mono uppercase"
                        >
                          {{ isAgentActive(msg.trace, 'search_catalog') ? 'Active' : 'Bypassed' }}
                        </Badge>
                      </div>

                      <!-- Review ABSA -->
                      <div
                        class="p-2 rounded-lg border flex items-center justify-between text-[11px]"
                        :class="isAgentActive(msg.trace, 'extract_reviews') ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-950 dark:text-emerald-100 font-medium' : 'bg-muted/30 border-dashed border-border/60 text-muted-foreground'"
                      >
                        <span>2. Review ABSA</span>
                        <Badge
                          :variant="isAgentActive(msg.trace, 'extract_reviews') ? 'verified' : 'outline'"
                          class="text-[9px] py-0 px-1 font-mono uppercase"
                        >
                          {{ isAgentActive(msg.trace, 'extract_reviews') ? 'Active' : 'Bypassed' }}
                        </Badge>
                      </div>

                      <!-- Formula Twins -->
                      <div
                        class="p-2 rounded-lg border flex items-center justify-between text-[11px]"
                        :class="isAgentActive(msg.trace, 'find_alternatives') ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-950 dark:text-emerald-100 font-medium' : 'bg-muted/30 border-dashed border-border/60 text-muted-foreground'"
                      >
                        <span>3. Formula Twins</span>
                        <Badge
                          :variant="isAgentActive(msg.trace, 'find_alternatives') ? 'verified' : 'outline'"
                          class="text-[9px] py-0 px-1 font-mono uppercase"
                        >
                          {{ isAgentActive(msg.trace, 'find_alternatives') ? 'Active' : 'Bypassed' }}
                        </Badge>
                      </div>

                      <!-- PubMed / FDA -->
                      <div
                        class="p-2 rounded-lg border flex items-center justify-between text-[11px]"
                        :class="isAgentActive(msg.trace, 'retrieve_references') ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-950 dark:text-emerald-100 font-medium' : 'bg-muted/30 border-dashed border-border/60 text-muted-foreground'"
                      >
                        <span>4. PubMed & FDA</span>
                        <Badge
                          :variant="isAgentActive(msg.trace, 'retrieve_references') ? 'verified' : 'outline'"
                          class="text-[9px] py-0 px-1 font-mono uppercase"
                        >
                          {{ isAgentActive(msg.trace, 'retrieve_references') ? 'Active' : 'Bypassed' }}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <!-- Section 3: Event Audit Log & Timeline with ScrollArea -->
                  <div v-if="msg.trace.events && msg.trace.events.length > 0" class="space-y-1.5">
                    <div class="text-[11px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                      <Clock class="w-3 h-3 text-primary" />
                      Event Audit Timeline ({{ msg.trace.events.length }} events)
                    </div>
                    <ScrollArea class="h-48 rounded-lg border p-2.5 bg-muted/20 font-mono text-[10px]">
                      <div class="space-y-1 pr-3">
                        <div
                          v-for="(evt, eIdx) in msg.trace.events"
                          :key="eIdx"
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
                          <span class="text-muted-foreground shrink-0">{{ formatEventTime(evt.timestamp) }}</span>
                        </div>
                      </div>
                    </ScrollArea>
                  </div>

                  <!-- Section 4: Stage Latencies -->
                  <div v-if="msg.trace.stage_timings_ms" class="flex items-center justify-between text-[10px] text-muted-foreground border-t border-border/40 pt-2 font-mono flex-wrap gap-2">
                    <div class="flex items-center gap-2">
                      <span>Interpret: <strong>{{ msg.trace.stage_timings_ms.interpret || 0 }}ms</strong></span>
                      <span>·</span>
                      <span>Search: <strong>{{ msg.trace.stage_timings_ms.search || 0 }}ms</strong></span>
                      <span>·</span>
                      <span>Evidence: <strong>{{ msg.trace.stage_timings_ms.evidence || 0 }}ms</strong></span>
                      <span>·</span>
                      <span>Synthesis: <strong>{{ msg.trace.stage_timings_ms.synthesis || 0 }}ms</strong></span>
                    </div>
                    <div class="font-bold text-foreground">
                      Total: {{ msg.trace.stage_timings_ms.elapsed_ms || msg.trace.elapsed_ms }}ms
                    </div>
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </div>
          <span class="text-[10px] text-muted-foreground px-1" :class="msg.role === 'user' ? 'text-right' : ''">
            {{ msg.timestamp }}
          </span>
        </div>
      </div>
    </div>

    <!-- Suggested Quick Prompts -->
    <div v-if="messages.length <= 2" class="p-3 border-t bg-muted/20 flex items-center gap-2 overflow-x-auto">
      <span class="text-[11px] font-bold text-muted-foreground shrink-0">Try asking:</span>
      <button
        v-for="prompt in samplePrompts"
        :key="prompt"
        class="text-xs px-3 py-1 rounded-full border bg-background hover:bg-muted text-foreground transition-colors shrink-0 cursor-pointer font-medium"
        @click="handleSend(prompt)"
      >
        {{ prompt }}
      </button>
    </div>

    <!-- Input Footer -->
    <div class="p-3.5 border-t flex items-center gap-2 bg-card">
      <Input
        v-model="queryInput"
        placeholder="Ask anything about cosmetic chemistry, barrier repair, skin sensitivity, reviews..."
        class="h-10 text-xs sm:text-sm flex-grow"
        :disabled="loading"
        @keydown.enter="handleSend()"
      />
      <Button
        variant="default"
        size="sm"
        class="h-10 px-4 gap-1.5 font-bold cursor-pointer"
        :disabled="!queryInput.trim() || loading"
        @click="handleSend()"
      >
        <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
        <Send v-else class="w-4 h-4" />
        Send
      </Button>
    </div>

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
