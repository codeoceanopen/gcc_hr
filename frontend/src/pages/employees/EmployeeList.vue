<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createListResource, FormControl } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Pagination from '@/components/ui/Pagination.vue'
import { complianceTone } from '@/utils/format'
import { useCompanyStore } from '@/stores/company'

const router = useRouter()
const route = useRoute()
const companyStore = useCompanyStore()

// Defaults to the globally-selected company (company-first context) but
// stays overridable here -- viewing other companies' employees is a normal,
// legitimate thing to do from this list, unlike the country-specific pages.
const filterState = reactive({
	search: (route.query.q as string) || '',
	status: '',
	company: companyStore.selectedCompany,
})

const COLUMNS: DataTableColumn[] = [
	{ key: 'employee_name', label: 'Employee' },
	{ key: 'company', label: 'Company' },
	{ key: 'country', label: 'Country' },
	{ key: 'compliance_score', label: 'Score', align: 'right' },
	{ key: 'compliance_status', label: 'Status' },
]

function buildFilters() {
	const filters: Record<string, any> = {}
	if (filterState.search) filters.employee_name = ['like', `%${filterState.search}%`]
	if (filterState.status) filters.compliance_status = filterState.status
	if (filterState.company) filters.company = filterState.company
	return filters
}

const profiles = createListResource({
	doctype: 'Employee Compliance Profile',
	fields: ['name', 'employee_name', 'company', 'country', 'compliance_score', 'compliance_status', 'nationality'],
	filters: buildFilters(),
	orderBy: 'compliance_score asc',
	pageLength: 20,
	auto: true,
})

// Follow the global company selector if it changes while on this page (e.g.
// bootstrap() resolves after mount, or the user switches company in the
// header) -- the local select below still lets them override it.
watch(
	() => companyStore.selectedCompany,
	(company) => {
		filterState.company = company
	},
)

let debounceTimer: ReturnType<typeof setTimeout>
watch(
	() => [filterState.search, filterState.status, filterState.company],
	() => {
		clearTimeout(debounceTimer)
		debounceTimer = setTimeout(() => {
			profiles.update({ filters: buildFilters() })
			profiles.reload()
		}, 300)
	},
)

function openEmployee(row: Record<string, any>) {
	router.push(`/employees/${row.name}`)
}
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'HR' }, { label: 'Employees' }]" />
		<PageHeader title="Employees" description="Manage employee compliance profiles, scores, and status." />

		<div class="p-6">
			<SectionCard no-padding>
				<div class="flex flex-wrap items-center gap-2 border-b border-app-border p-3">
					<div class="w-full max-w-xs">
						<SearchInput v-model="filterState.search" placeholder="Search employees..." />
					</div>
					<FormControl
						v-model="filterState.status"
						type="select"
						variant="outline"
						class="w-40"
						:options="['', 'Compliant', 'Warning', 'Critical', 'Blocked']"
					/>
					<FormControl
						v-model="filterState.company"
						type="select"
						variant="outline"
						class="w-48"
						:options="[
							{ label: 'All Companies', value: '' },
							...companyStore.companies.map((c) => ({ label: c.company, value: c.company })),
						]"
					/>
					<span class="ml-auto text-[13px] leading-[16px] text-app-muted">
						{{ profiles.data?.length || 0 }} {{ profiles.data?.length === 1 ? 'employee' : 'employees' }}
					</span>
				</div>

				<DataTable
					:columns="COLUMNS"
					:rows="profiles.data || []"
					:loading="profiles.loading"
					clickable-rows
					empty-title="No employees found"
					empty-description="There are no employees matching your filters."
					@row-click="openEmployee"
				>
					<template #cell-employee_name="{ row }">
						<span class="font-medium text-app-text">{{ row.employee_name }}</span>
					</template>
					<template #cell-company="{ row }">{{ row.company || '—' }}</template>
					<template #cell-country="{ row }">{{ row.country || '—' }}</template>
					<template #cell-compliance_score="{ row }">{{ row.compliance_score }}%</template>
					<template #cell-compliance_status="{ row }">
						<StatusBadge :label="row.compliance_status" :tone="complianceTone(row.compliance_status)" />
					</template>
				</DataTable>

				<Pagination v-if="profiles.data?.length" :resource="profiles" />
			</SectionCard>
		</div>
	</div>
</template>
