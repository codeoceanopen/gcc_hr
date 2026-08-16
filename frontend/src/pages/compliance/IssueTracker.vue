<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createListResource } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { documentStatusTone } from '@/utils/format'
import { useCompanyStore } from '@/stores/company'

const companyStore = useCompanyStore()

const filterState = reactive({ company: companyStore.selectedCompany })

const DOCUMENT_COLUMNS: DataTableColumn[] = [
	{ key: 'employee_name', label: 'Employee' },
	{ key: 'document_type', label: 'Document Type' },
	{ key: 'expiry_date', label: 'Expiry' },
	{ key: 'days_remaining', label: 'Days', align: 'right' },
	{ key: 'status', label: 'Status' },
]

const CONTRACT_COLUMNS: DataTableColumn[] = [
	{ key: 'party_name', label: 'Employee' },
	{ key: 'end_date', label: 'Ended' },
	{ key: 'status', label: 'Status' },
]

function buildDocumentFilters() {
	const filters: Record<string, any> = { status: ['in', ['Expired', 'Expiring Soon']] }
	if (filterState.company) filters.company = filterState.company
	return filters
}

const expiringDocuments = createListResource({
	doctype: 'HR Compliance Document',
	fields: ['name', 'employee_name', 'document_type', 'expiry_date', 'days_remaining', 'status'],
	filters: buildDocumentFilters(),
	orderBy: 'days_remaining asc',
	pageLength: 50,
	auto: true,
})

// Contract has no `company` field (standard ERPNext CRM doctype, party_type
// scoped only) -- this list is intentionally site-wide, not company-filtered,
// same limitation noted in api/dashboard.py's _get_recent_critical_issues.
const expiredContracts = createListResource({
	doctype: 'Contract',
	fields: ['name', 'party_name', 'end_date', 'status'],
	filters: { party_type: 'Employee', end_date: ['<', new Date().toISOString().slice(0, 10)] },
	orderBy: 'end_date desc',
	pageLength: 50,
	auto: true,
})

watch(
	() => companyStore.selectedCompany,
	(company) => {
		filterState.company = company
		expiringDocuments.update({ filters: buildDocumentFilters() })
		expiringDocuments.reload()
	},
)
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'Compliance' }, { label: 'Issue Tracker' }]" />
		<PageHeader
			title="Issue Tracker"
			description="Expiring or expired documents and contracts that need attention."
		/>

		<div class="space-y-4 p-6">
			<SectionCard title="Documents Expiring or Expired" no-padding>
				<DataTable
					:columns="DOCUMENT_COLUMNS"
					:rows="expiringDocuments.data || []"
					:loading="expiringDocuments.loading"
					empty-title="Nothing expiring"
					empty-description="No documents are expiring or expired for this company."
				>
					<template #cell-employee_name="{ row }">
						<span class="font-medium text-app-text">{{ row.employee_name }}</span>
					</template>
					<template #cell-status="{ row }">
						<StatusBadge :label="row.status" :tone="documentStatusTone(row.status)" />
					</template>
				</DataTable>
			</SectionCard>

			<SectionCard
				title="Expired Contracts"
				description="Site-wide -- Contract has no company field, so this can't be scoped to the selected company."
				no-padding
			>
				<DataTable
					:columns="CONTRACT_COLUMNS"
					:rows="expiredContracts.data || []"
					:loading="expiredContracts.loading"
					empty-title="No expired contracts"
					empty-description="There are no expired employment contracts."
				>
					<template #cell-party_name="{ row }">
						<span class="font-medium text-app-text">{{ row.party_name }}</span>
					</template>
					<template #cell-status="{ row }">
						<StatusBadge :label="row.status" :tone="row.status === 'Active' ? 'success' : 'neutral'" />
					</template>
				</DataTable>
			</SectionCard>
		</div>
	</div>
</template>
