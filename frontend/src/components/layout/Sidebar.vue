<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
	LayoutDashboard,
	Users,
	FileText,
	ShieldCheck,
	ListChecks,
	FileSignature,
	Wallet,
	Landmark,
	Building2,
	Percent,
	Globe,
	Building,
} from 'lucide-vue-next'
import { NAV_SECTIONS, CURRENT_PHASE } from '@/router/nav'
import { useCompanyStore } from '@/stores/company'

const route = useRoute()
const companyStore = useCompanyStore()

// Country-tagged sections (Saudi Arabia, Qatar, ...) only show while the
// globally-selected company is actually configured for that country -- see
// nav.ts's NavSection.country doc comment. Sections without a `country` tag
// (Overview/Employees/.../Settings) always show.
const visibleSections = computed(() =>
	NAV_SECTIONS.filter((section) => !section.country || section.country === companyStore.selectedCountry),
)
const scrollSections = computed(() => visibleSections.value.filter((s) => !s.pinned))
const pinnedSections = computed(() => visibleSections.value.filter((s) => s.pinned))

// Resolved by the string names used in nav.ts -- keeps nav.ts free of
// component imports (it's plain data, shared with the router table too).
const ICONS: Record<string, unknown> = {
	LayoutDashboard,
	Users,
	FileText,
	ShieldCheck,
	ListChecks,
	FileSignature,
	Wallet,
	Landmark,
	Building2,
	Percent,
	Globe,
	Building,
}
</script>

<template>
	<aside class="flex w-56 shrink-0 flex-col border-r border-app-border bg-app-surface">
		<div class="flex h-[56px] shrink-0 items-center border-b border-app-border px-4">
			<span class="text-[14px] font-semibold leading-[20px] text-app-text">GCC HR</span>
		</div>
		<nav class="flex-1 space-y-4 overflow-y-auto px-2 py-3">
			<div v-for="section in scrollSections" :key="section.label">
				<div class="px-2 pb-1 text-[11px] font-semibold uppercase leading-[16px] tracking-wide text-app-muted">
					{{ section.label }}
				</div>
				<router-link
					v-for="item in section.items"
					:key="item.route"
					:to="item.route"
					class="mt-0.5 flex items-center justify-between gap-2 rounded-app-sm px-2 py-1.5 text-[13px] leading-[16px]"
					:class="
						route.path === item.route
							? 'bg-app-primary-surface font-medium text-app-primary'
							: 'text-app-text hover:bg-app-bg'
					"
				>
					<span class="flex min-w-0 items-center gap-2">
						<component :is="ICONS[item.icon]" :size="16" class="shrink-0" />
						<span class="truncate">{{ item.label }}</span>
					</span>
					<span
						v-if="item.comingInPhase && item.comingInPhase > CURRENT_PHASE"
						class="shrink-0 rounded bg-app-warning-surface px-1.5 py-0.5 text-[10px] leading-[12px] text-app-warning"
					>
						Phase {{ item.comingInPhase }}
					</span>
				</router-link>
			</div>
		</nav>

		<div v-if="pinnedSections.length" class="shrink-0 border-t border-app-border px-2 py-3">
			<div v-for="section in pinnedSections" :key="section.label">
				<div class="px-2 pb-1 text-[11px] font-semibold uppercase leading-[16px] tracking-wide text-app-muted">
					{{ section.label }}
				</div>
				<router-link
					v-for="item in section.items"
					:key="item.route"
					:to="item.route"
					class="mt-0.5 flex items-center justify-between gap-2 rounded-app-sm px-2 py-1.5 text-[13px] leading-[16px]"
					:class="
						route.path === item.route
							? 'bg-app-primary-surface font-medium text-app-primary'
							: 'text-app-text hover:bg-app-bg'
					"
				>
					<span class="flex min-w-0 items-center gap-2">
						<component :is="ICONS[item.icon]" :size="16" class="shrink-0" />
						<span class="truncate">{{ item.label }}</span>
					</span>
				</router-link>
			</div>
		</div>
	</aside>
</template>
