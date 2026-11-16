import { createApp } from 'vue'
import './assets/index.css'
import App from './App.vue'
import router, { recoverFromStaleChunk } from './router'

const app = createApp(App).use(router)
// reka-ui loads some components through its own dynamic imports, outside
// vue-router — a stale client 404s on those too. Same one-shot recovery as
// the router guard (shared sessionStorage flag); anything else logs.
app.config.errorHandler = (err) => {
  if (!recoverFromStaleChunk(err)) console.error(err)
}
app.mount('#app')
