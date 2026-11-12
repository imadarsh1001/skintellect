import { createRouter, createWebHistory } from 'vue-router'
import CompareView from '@/views/CompareView.vue'
import CopilotView from '@/views/CopilotView.vue'
import ExploreView from '@/views/ExploreView.vue'
import GraphView from '@/views/GraphView.vue'
import PrimitiveScratch from '@/views/PrimitiveScratch.vue'
import ProgressView from '@/views/ProgressView.vue'
import ResearchView from '@/views/ResearchView.vue'
import StudyView from '@/views/StudyView.vue'

/**
 * One SPA route per workspace. Legacy hash deep links (`/#copilot`,
 * `/#compare`, `/#graph`) redirect to their path equivalents in
 * `beforeEach` so existing bookmarks and the legacy workspace nav
 * keep working. /research, /study and /progress replace the retired
 * legacy template pages (Stage 5), honoring `?query=` and `?demo=1`
 * carry-over inside ResearchView.
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'explore', component: ExploreView },
    { path: '/compare', name: 'compare', component: CompareView },
    { path: '/graph', name: 'graph', component: GraphView },
    { path: '/copilot', name: 'copilot', component: CopilotView },
    { path: '/research', name: 'research', component: ResearchView },
    { path: '/study', name: 'study', component: StudyView },
    { path: '/progress', name: 'progress', component: ProgressView },
    { path: '/dev-primitives', name: 'dev-primitives', component: PrimitiveScratch }, // TEMP scratch (task 1.1/1.3), removed before commit
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

export default router
