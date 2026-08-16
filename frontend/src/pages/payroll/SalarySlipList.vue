<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createListResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Pagination from '@/components/ui/Pagination.vue'
import { useCompanyStore } from '@/stores/company'

const router = useRouter()
const companyStore = useCompanyStore()

const filterState = reactive({ search: '', company: companyStore.selectedCompany })

const COLUMNS: DataTableColumn[] = [
	{ key: 'employee_name', label: 'Employee' },
	{ key: 'start_date', label: 'Period' },
	{ key: 'gross_pay', label: 'Gross Pay', align: 'right' },
	{ key: 'net_pay', label: 'Net Pay', align: 'right' },
	{ key: 'status', label: 'Status' },
]

function buildFilters() {
	const filters: Record<string, any> = {}
	if (filterState.search) filters.employee_name = ['like', `%${filterState.search}%`]
	if (filterState.company) filters.company = filterState.company
	return filters
}

const salarySlips = createListResource({
	doctype: 'Salary Slip',
	fields: ['name', 'employee_name', 'company', 'start_date', 'end_date', 'gross_pay', 'net_pay', 'status'],
	filters: buildFilters(),
	orderBy: 'posting_date desc',
	pageLength: 20,
	auto: true,
})

watch(
	() => companyStore.selectedCompany,
	(company) => (filterState.company = company),
)

let debounceTimer: ReturnType<typeof setTimeout>
watch(
	() => [filterState.search, filterState.company],
	() => {
		clearTimeout(debounceTimer)
		debounceTimer = setTimeout(() => {
			salarySlips.update({ filters: buildFilters() })
			salarySlips.reload()
		}, 300)
	},
)

function statusTone(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
	if (status === 'Submitted') return 'success'
	if (status === 'Cancelled') return 'danger'
	if (status === 'Withheld') return 'warning'
	return 'neutral'
}

function openSlip(row: Record<string, any>) {
	router.push(`/app/salary-slip/${row.name}`)
}
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'Payroll' }, { label: 'Salary Slips' }]" />
		<PageHeader title="Salary Slips" description="Standard HRMS Salary Slip records, scoped to the selected company." />

		<div class="p-6">
			<SectionCard no-padding>
				<div class="flex flex-wrap items-center gap-2 border-b border-app-border p-3">
					<div class="w-full max-w-xs">
						<SearchInput v-model="filterState.search" placeholder="Search employees..." />
					</div>
					<span class="ml-auto text-[13px] leading-[16px] text-app-muted">
						{{ salarySlips.data?.length || 0 }} {{ salarySlips.data?.length === 1 ? 'slip' : 'slips' }}
					</span>
				</div>

				<DataTable
					:columns="COLUMNS"
					:rows="salarySlips.data || []"
					:loading="salarySlips.loading"
					clickable-rows
					empty-title="No salary slips found"
					empty-description="There are no salary slips matching your filters."
					@row-click="openSlip"
				>
					<template #cell-employee_name="{ row }">
						<span class="font-medium text-app-text">{{ row.employee_name }}</span>
					</template>
					<template #cell-start_date="{ row }">{{ row.start_date }} – {{ row.end_date }}</template>
					<template #cell-gross_pay="{ row }">{{ row.gross_pay }}</template>
					<template #cell-net_pay="{ row }">{{ row.net_pay }}</template>
					<template #cell-status="{ row }">
						<StatusBadge :label="row.status" :tone="statusTone(row.status)" />
					</template>
				</DataTable>

				<Pagination v-if="salarySlips.data?.length" :resource="salarySlips" />
			</SectionCard>
		</div>
	</div>
</template>
