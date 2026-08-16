import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { setConfig, frappeRequest } from 'frappe-ui'
import App from './App.vue'
import router from './router'
import { useSessionStore } from '@/stores/session'
import { useCompanyStore } from '@/stores/company'
import './style.css'

// frappe-ui's createResource/createListResource/createDocumentResource all
// fall back to a bare `fetch(options.url)` (utils/request.js) unless a
// resourceFetcher is configured -- without this, a relative url like
// 'frappe.client.get_list' resolves against the current SPA route (e.g.
// /gcc_hr/employees) instead of the site root, and every list/resource call
// 404s. frappeRequest is the fetcher that actually prefixes /api/method/.
setConfig('resourceFetcher', frappeRequest)

// The backend (gcc_hr/www/gcc_hr.py) serves this SPA shell to Guests too
// now (window.user = "Guest" in that case) -- the router's own
// beforeEach guard (router/index.ts) is what sends an unauthenticated user
// to the /login route, not a server-side redirect.
const app = createApp(App)
app.use(createPinia())

useSessionStore().bootstrap()
useCompanyStore().bootstrap()

app.use(router)
app.mount('#gcc-hr-app')
