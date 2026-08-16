<script setup lang="ts">
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { Building2, ChevronDown } from 'lucide-vue-next'
import { useCompanyStore } from '@/stores/company'

const companyStore = useCompanyStore()

const menuOpen = ref(false)
const menu = ref(null)
onClickOutside(menu, () => (menuOpen.value = false))

function selectCompany(company: string) {
	companyStore.selectCompany(company)
	menuOpen.value = false
}
</script>

<template>
	<div class="flex items-center gap-2">
		<div ref="menu" class="relative">
			<button
				type="button"
				class="flex items-center gap-1.5 rounded-app-sm border border-app-border bg-app-surface px-2.5 py-1.5 text-[13px] leading-[16px] text-app-text hover:bg-app-bg"
				@click="menuOpen = !menuOpen"
			>
				<Building2 :size="14" class="shrink-0 text-app-muted" />
				<span class="max-w-[160px] truncate font-medium">{{ companyStore.selectedCompany || 'Select company' }}</span>
				<ChevronDown :size="14" class="shrink-0 text-app-muted" />
			</button>
			<div
				v-if="menuOpen"
				class="absolute right-0 top-10 z-10 max-h-72 w-64 overflow-y-auto rounded-app-md border border-app-border bg-app-surface py-1 shadow-lg"
			>
				<button
					v-for="c in companyStore.companies"
					:key="c.company"
					type="button"
					class="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-[13px] leading-[16px] hover:bg-app-bg"
					:class="c.company === companyStore.selectedCompany ? 'font-medium text-app-primary' : 'text-app-text'"
					@click="selectCompany(c.company)"
				>
					<span class="truncate">{{ c.company }}</span>
					<span class="shrink-0 text-[12px] text-app-muted">{{ c.country }}</span>
				</button>
				<div v-if="!companyStore.companies.length" class="px-3 py-4 text-center text-[13px] text-app-muted">
					No companies configured yet.
				</div>
			</div>
		</div>

		<span
			v-if="companyStore.selectedCountry"
			class="shrink-0 rounded-app-sm bg-app-primary-surface px-2 py-1.5 text-[12px] font-medium leading-[16px] text-app-primary"
		>
			{{ companyStore.selectedCountry }}
		</span>
	</div>
</template>
