import { createRouter, createWebHistory } from 'vue-router'

// Route components load lazily (one chunk per view) so the first paint
// only downloads the entry + landing view, not the whole SPA.
const CompareView = () => import('@/views/CompareView.vue')
const CopilotView = () => import('@/views/CopilotView.vue')
const ExploreView = () => import('@/views/ExploreView.vue')
const GraphView = () => import('@/views/GraphView.vue')
const HomeView = () => import('@/views/HomeView.vue')
const ProgressView = () => import('@/views/ProgressView.vue')
const ResearchView = () => import('@/views/ResearchView.vue')
const StudyView = () => import('@/views/StudyView.vue')

/**
 * One SPA route per workspace, plus the landing home at `/` (the
 * catalog lives at `/explore`). Legacy hash deep links (`/#copilot`,
 * `/#compare`, `/#graph`) redirect to their path equivalents in
 * `beforeEach` so existing bookmarks and the legacy workspace nav
 * keep working. /research, /study and /progress replace the retired
 * legacy template pages (Stage 5), honoring `?query=` and `?demo=1`
 * carry-over inside ResearchView.
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/explore', name: 'explore', component: ExploreView },
    { path: '/compare', name: 'compare', component: CompareView },
    { path: '/graph', name: 'graph', component: GraphView },
    { path: '/copilot', name: 'copilot', component: CopilotView },
    { path: '/research', name: 'research', component: ResearchView },
    { path: '/study', name: 'study', component: StudyView },
    { path: '/progress', name: 'progress', component: ProgressView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

const HASH_ROUTES: Record<string, string> = {
  copilot: '/copilot',
  research: '/copilot',
  chat: '/copilot',
  compare: '/compare',
  graph: '/graph',
}

router.beforeEach((to) => {
  if (to.path === '/' && to.hash) {
    const target = HASH_ROUTES[to.hash.slice(1).toLowerCase()]
    if (target) return { path: target, query: to.query, hash: '' }
  }
  return true
})

// One-shot stale-chunk recovery, shared by the router guard and the
// app-level errorHandler: a deploy between visits changes chunk hashes, so
// a client holding the old index 404s on a lazy chunk it tries to load.
// One hard navigation picks up the new build. The sessionStorage flag makes
// the recovery once-per-failure so a genuinely broken deploy surfaces its
// error instead of looping. NOTE: dynamic-import errors carry no HTTP
// status, so the regexes can't tell a stale-hash 404 from an offline blip —
// a transient failure also costs one reload. Acceptable: the state that
// survives reload (persona, compare tray) lives in localStorage.
const CHUNK_LOAD_ERROR =
  /Failed to fetch dynamically imported module|Importing a module script failed|error loading dynamically imported module/

export function recoverFromStaleChunk(error: unknown, targetPath?: string): boolean {
  if (
    !CHUNK_LOAD_ERROR.test(String((error as Error)?.message ?? '')) ||
    sessionStorage.getItem('skintellect_chunk_reload') !== null
  ) {
    return false
  }
  sessionStorage.setItem('skintellect_chunk_reload', '1')
  window.location.assign(
    targetPath ?? window.location.pathname + window.location.search + window.location.hash,
  )
  return true
}

router.onError((error, to) => {
  recoverFromStaleChunk(error, to?.fullPath)
})
router.afterEach(() => sessionStorage.removeItem('skintellect_chunk_reload'))

export default router
