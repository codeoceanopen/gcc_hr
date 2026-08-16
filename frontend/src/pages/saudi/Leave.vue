<script setup lang="ts">
import { computed, watch } from 'vue'
import { createListResource, createResource } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import { useCompanyStore } from '@/stores/company'

const companyStore = useCompanyStore()

const ENTITLEMENT_COLUMNS: DataTableColumn[] = [
	{ key: 'employee_name', label: 'Employee' },
	{ key: 'entitlement_days', label: 'Entitlement', align: 'right' },
	{ key: 'allocated_days', label: 'Allocated', align: 'right' },
	{ key: 'carried_forward_days', label: 'Carried Forward', align: 'right' },
	{ key: 'status', label: 'Status' },
]

const ENCASHMENT_COLUMNS: DataTableColumn[] = [
	{ key: 'employee_name', label: 'Employee' },
	{ key: 'encashment_days', label: 'Days', align: 'right' },
	{ key: 'encashment_amount', label: 'Amount', align: 'right' },
	{ key: 'status', label: 'Status' },
]

const summary = createResource({
	url: 'gcc_hr.api.leave.get_leave_summary',
	params: { company: companyStore.selectedCompany },
	auto: false,
})

const encashments = createListResource({
	doctype: 'Leave Encashment',
	fields: ['name', 'employee_name', 'encashment_days', 'encashment_amount', 'status'],
	filters: companyStore.selectedCompany ? { company: companyStore.selectedCompany } : {},
	orderBy: 'modified desc',
	pageLength: 50,
	auto: true,
})

watch(
	() => [companyStore.selectedCompany, companyStore.selectedCountry] as const,
	([company, country]) => {
		if (!company || country !== 'Saudi Arabia') return
		summary.update({ params: { company } })
		summary.reload()
		encashments.update({ filters: { company } })
		encashments.reload()
	},
	{ immediate: true },
)

const rows = computed(() =>
	(summary.data || []).map((row: any) => ({
		...row,
		status: !row.has_allocation ? 'No Allocation' : row.allocated_days >= row.entitlement_days ? 'Compliant' : 'Below Entitlement',
	})),
)

function statusTone(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
	if (status === 'Compliant') return 'success'
	if (status === 'Below Entitlement') return 'warning'
	if (status === 'No Allocation') return 'neutral'
	if (status === 'Paid' || status === 'Submitted') return 'success'
	return 'neutral'
}
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'Saudi Arabia' }, { label: 'Leave' }]" />
		<PageHeader
			title="Annual Leave"
			description="Entitlement (KSA Labour Law Art. 109), carry-forward, and encashment for the selected company -- backed by HRMS's own Leave Type/Leave Allocation/Leave Encashment engine."
		/>

		<div class="space-y-4 p-6">
			<div v-if="companyStore.selectedCountry !== 'Saudi Arabia'" class="py-12 text-center text-[13px] text-app-muted">
				Select a Saudi Arabia company from the header to view leave entitlement and carry-forward.
			</div>

			<template v-else>
				<LoadingState v-if="summary.loading && !summary.data" />

				<SectionCard v-else title="Entitlement &amp; Carry Forward" no-padding>
					<DataTable
						:columns="ENTITLEMENT_COLUMNS"
						:rows="rows"
						empty-title="No employees found"
						empty-description="There are no active employees for this company."
					>
						<template #cell-employee_name="{ row }">
							<span class="font-medium text-app-text">{{ row.employee_name }}</span>
						</template>
						<template #cell-entitlement_days="{ row }">{{ row.entitlement_days }} days</template>
						<template #cell-allocated_days="{ row }">
							{{ row.allocated_days !== null ? `${row.allocated_days} days` : '—' }}
						</template>
						<template #cell-carried_forward_days="{ row }">{{ row.carried_forward_days || 0 }} days</template>
						<template #cell-status="{ row }">
							<StatusBadge :label="row.status" :tone="statusTone(row.status)" />
						</template>
					</DataTable>
				</SectionCard>

				<SectionCard title="Leave Encashment" no-padding>
					<DataTable
						:columns="ENCASHMENT_COLUMNS"
						:rows="encashments.data || []"
						:loading="encashments.loading"
						empty-title="No encashment records"
						empty-description="No leave has been cashed out for this company yet."
					>
						<template #cell-employee_name="{ row }">
							<span class="font-medium text-app-text">{{ row.employee_name }}</span>
						</template>
						<template #cell-encashment_days="{ row }">{{ row.encashment_days }} days</template>
						<template #cell-encashment_amount="{ row }">{{ row.encashment_amount }}</template>
						<template #cell-status="{ row }">
							<StatusBadge :label="row.status" :tone="statusTone(row.status)" />
						</template>
					</DataTable>
				</SectionCard>
			</template>
		</div>
	</div>
</template>
