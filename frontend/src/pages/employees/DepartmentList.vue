<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createListResource } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Pagination from '@/components/ui/Pagination.vue'
import { useCompanyStore } from '@/stores/company'

const companyStore = useCompanyStore()

const filterState = reactive({ search: '', company: companyStore.selectedCompany })

const COLUMNS: DataTableColumn[] = [
	{ key: 'department_name', label: 'Department' },
	{ key: 'company', label: 'Company' },
	{ key: 'is_group', label: 'Type' },
	{ key: 'disabled', label: 'Status' },
]

function buildFilters() {
	const filters: Record<string, any> = {}
	if (filterState.search) filters.department_name = ['like', `%${filterState.search}%`]
	if (filterState.company) filters.company = filterState.company
	return filters
}

const departments = createListResource({
	doctype: 'Department',
	fields: ['name', 'department_name', 'company', 'is_group', 'disabled'],
	filters: buildFilters(),
	orderBy: 'department_name asc',
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
			departments.update({ filters: buildFilters() })
			departments.reload()
		}, 300)
	},
)
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'HR' }, { label: 'Departments' }]" />
		<PageHeader title="Departments" description="Standard ERPNext Department records, scoped to the selected company." />

		<div class="p-6">
			<SectionCard no-padding>
				<div class="flex flex-wrap items-center gap-2 border-b border-app-border p-3">
					<div class="w-full max-w-xs">
						<SearchInput v-model="filterState.search" placeholder="Search departments..." />
					</div>
					<span class="ml-auto text-[13px] leading-[16px] text-app-muted">
						{{ departments.data?.length || 0 }} {{ departments.data?.length === 1 ? 'department' : 'departments' }}
					</span>
				</div>

				<DataTable
					:columns="COLUMNS"
					:rows="departments.data || []"
					:loading="departments.loading"
					empty-title="No departments found"
					empty-description="There are no departments matching your filters."
				>
					<template #cell-department_name="{ row }">
						<span class="font-medium text-app-text">{{ row.department_name }}</span>
					</template>
					<template #cell-company="{ row }">{{ row.company || '—' }}</template>
					<template #cell-is_group="{ row }">{{ row.is_group ? 'Group' : 'Department' }}</template>
					<template #cell-disabled="{ row }">
						<StatusBadge :label="row.disabled ? 'Disabled' : 'Active'" :tone="row.disabled ? 'neutral' : 'success'" />
					</template>
				</DataTable>

				<Pagination v-if="departments.data?.length" :resource="departments" />
			</SectionCard>
		</div>
	</div>
</template>
