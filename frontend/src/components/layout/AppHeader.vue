<script setup lang="ts">
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { useRouter } from 'vue-router'
import { createListResource } from 'frappe-ui'
import { Bell } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import SearchInput from '@/components/ui/SearchInput.vue'

const router = useRouter()
const session = useSessionStore()

const searchQuery = ref('')
function runSearch() {
	if (!searchQuery.value.trim()) return
	router.push({ path: '/employees', query: { q: searchQuery.value.trim() } })
}

// Real, if modest, notification feed: the latest Critical compliance
// checks -- reuses data this app already computes (the compliance engine's
// own run history), rather than a separate notification system that
// doesn't exist yet. See DESIGN.md for why this is intentionally scoped
// down from a full cross-entity notification center.
const criticalChecks = createListResource({
	doctype: 'HR Compliance Check',
	fields: ['name', 'employee_name', 'status', 'critical_issues', 'check_date'],
	filters: { status: 'Critical' },
	orderBy: 'check_date desc',
	pageLength: 5,
	auto: true,
})

const notificationsOpen = ref(false)
const notificationsPanel = ref(null)
onClickOutside(notificationsPanel, () => (notificationsOpen.value = false))

const userMenuOpen = ref(false)
const userMenu = ref(null)
onClickOutside(userMenu, () => (userMenuOpen.value = false))
</script>

<template>
	<header class="flex h-[56px] shrink-0 items-center gap-4 border-b border-app-border bg-app-surface px-4 sm:px-6">
		<div class="max-w-md flex-1">
			<SearchInput v-model="searchQuery" placeholder="Search employees, documents, contracts..." @keyup.enter="runSearch" />
		</div>

		<div class="ml-auto flex shrink-0 items-center gap-2">
			<div ref="notificationsPanel" class="relative">
				<button
					type="button"
					class="relative flex h-8 w-8 items-center justify-center rounded-app-sm text-app-muted hover:bg-app-bg hover:text-app-text"
					@click="notificationsOpen = !notificationsOpen"
				>
					<Bell :size="18" />
					<span
						v-if="criticalChecks.data?.length"
						class="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-app-danger"
					/>
				</button>
				<div
					v-if="notificationsOpen"
					class="absolute right-0 top-10 z-10 w-80 rounded-app-md border border-app-border bg-app-surface py-2 shadow-lg"
				>
					<p class="px-3 pb-2 text-[13px] font-semibold leading-[16px] text-app-text">Notifications</p>
					<div v-if="!criticalChecks.data?.length" class="px-3 py-4 text-center text-[13px] text-app-muted">
						No critical notifications.
					</div>
					<div
						v-for="check in criticalChecks.data"
						:key="check.name"
						class="border-t border-app-border px-3 py-2 first:border-t-0"
					>
						<p class="text-[13px] font-medium leading-[16px] text-app-text">
							{{ check.critical_issues }} critical issue(s)
						</p>
						<p class="mt-0.5 text-[13px] leading-[16px] text-app-muted">{{ check.employee_name }}</p>
						<p class="mt-0.5 text-[12px] leading-[16px] text-app-disabled">{{ check.check_date }}</p>
					</div>
				</div>
			</div>

			<div ref="userMenu" class="relative">
				<button
					type="button"
					class="flex items-center gap-2 rounded-app-sm px-1.5 py-1 hover:bg-app-bg"
					@click="userMenuOpen = !userMenuOpen"
				>
					<span class="flex h-7 w-7 items-center justify-center rounded-full bg-app-text text-[12px] font-medium text-white">
						{{ session.initials }}
					</span>
					<span class="hidden text-[13px] font-medium leading-[16px] text-app-text sm:inline">{{ session.fullName }}</span>
				</button>
				<div
					v-if="userMenuOpen"
					class="absolute right-0 top-10 z-10 w-44 rounded-app-md border border-app-border bg-app-surface py-1 shadow-lg"
				>
					<button
						type="button"
						class="block w-full px-3 py-2 text-left text-[13px] leading-[16px] text-app-text hover:bg-app-bg"
						@click="session.logout()"
					>
						Log out
					</button>
				</div>
			</div>
		</div>
	</header>
</template>
