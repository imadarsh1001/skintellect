import { createRouter, createWebHistory } from 'vue-router'
import CompareView from '@/views/CompareView.vue'
import CopilotView from '@/views/CopilotView.vue'
import ExploreView from '@/views/ExploreView.vue'
import GraphView from '@/views/GraphView.vue'

/**
 * One SPA route per workspace. Legacy hash deep links (`/#copilot`,
 * `/#compare`, `/#graph`) redirect to their path equivalents in
 * `beforeEach` so existing bookmarks and the legacy workspace nav
 * keep working. `/research` historically activated the copilot tab
 * in the SPA (App.vue read the pathname), so it redirects to /copilot
 * until the structured evidence route lands (Stage 5).
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'explore', component: ExploreView },
    { path: '/compare', name: 'compare', component: CompareView },
    { path: '/graph', name: 'graph', component: GraphView },
    { path: '/copilot', name: 'copilot', component: CopilotView },
    { path: '/research', redirect: '/copilot' },
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
