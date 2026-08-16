<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createListResource } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import SearchInput from '@/components/ui/SearchInput.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import Pagination from '@/components/ui/Pagination.vue'

const filterState = reactive({ search: '' })

const COLUMNS: DataTableColumn[] = [
	{ key: 'designation_name', label: 'Designation' },
	{ key: 'description', label: 'Description' },
]

const designations = createListResource({
	doctype: 'Designation',
	fields: ['name', 'designation_name', 'description'],
	orderBy: 'designation_name asc',
	pageLength: 20,
	auto: true,
})

let debounceTimer: ReturnType<typeof setTimeout>
watch(
	() => filterState.search,
	() => {
		clearTimeout(debounceTimer)
		debounceTimer = setTimeout(() => {
			designations.update({
				filters: filterState.search ? { designation_name: ['like', `%${filterState.search}%`] } : {},
			})
			designations.reload()
		}, 300)
	},
)
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'HR' }, { label: 'Designations' }]" />
		<PageHeader title="Designations" description="Standard ERPNext Designation records -- shared across all companies." />

		<div class="p-6">
			<SectionCard no-padding>
				<div class="flex flex-wrap items-center gap-2 border-b border-app-border p-3">
					<div class="w-full max-w-xs">
						<SearchInput v-model="filterState.search" placeholder="Search designations..." />
					</div>
					<span class="ml-auto text-[13px] leading-[16px] text-app-muted">
						{{ designations.data?.length || 0 }} {{ designations.data?.length === 1 ? 'designation' : 'designations' }}
					</span>
				</div>

				<DataTable
					:columns="COLUMNS"
					:rows="designations.data || []"
					:loading="designations.loading"
					empty-title="No designations found"
					empty-description="There are no designations matching your filters."
				>
					<template #cell-designation_name="{ row }">
						<span class="font-medium text-app-text">{{ row.designation_name }}</span>
					</template>
					<template #cell-description="{ row }">{{ row.description || '—' }}</template>
				</DataTable>

				<Pagination v-if="designations.data?.length" :resource="designations" />
			</SectionCard>
		</div>
	</div>
</template>
