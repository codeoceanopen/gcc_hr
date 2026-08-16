<script setup lang="ts">
import { watch } from 'vue'
import { createListResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { governmentSubmissionTone } from '@/utils/format'
import { useCompanyStore } from '@/stores/company'

const router = useRouter()
const companyStore = useCompanyStore()

// Reuses the existing, real Government Submission doctype (same data as the
// site-wide /government page) filtered to the selected Saudi company --
// there's no dedicated "WPS" submission type seeded yet (only Nitaqat Report
// and GOSI Registration Summary), so this deliberately shows the company's
// full submission history rather than fabricating a WPS-only filter.
const COLUMNS: DataTableColumn[] = [
	{ key: 'submission_type', label: 'Submission Type' },
	{ key: 'status', label: 'Status' },
	{ key: 'outcome', label: 'Outcome' },
	{ key: 'generated_on', label: 'Generated' },
	{ key: 'submitted_on', label: 'Submitted' },
]

const submissions = createListResource({
	doctype: 'Government Submission',
	fields: ['name', 'submission_type', 'status', 'outcome', 'generated_on', 'submitted_on'],
	filters: companyStore.selectedCompany ? { company: companyStore.selectedCompany } : {},
	orderBy: 'modified desc',
	pageLength: 50,
	auto: true,
})

watch(
	() => companyStore.selectedCompany,
	(company) => {
		if (!company) return
		submissions.update({ filters: { company } })
		submissions.reload()
	},
)

function openSubmission(row: Record<string, any>) {
	router.push(`/government/${row.name}`)
}
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'Saudi Arabia' }, { label: 'WPS / Government Filing' }]" />
		<PageHeader
			title="WPS / Government Filing"
			description="Government submissions for the selected company -- Wage Protection filings, Nitaqat reports, and GOSI registration summaries."
		/>

		<div class="p-6">
			<SectionCard v-if="companyStore.selectedCountry !== 'Saudi Arabia'" title="WPS / Government Filing">
				<p class="py-6 text-center text-[13px] text-app-muted">
					Select a Saudi Arabia company from the header to view its government filings.
				</p>
			</SectionCard>

			<SectionCard v-else no-padding>
				<DataTable
					:columns="COLUMNS"
					:rows="submissions.data || []"
					:loading="submissions.loading"
					clickable-rows
					empty-title="No submissions yet"
					empty-description="No government submissions have been created for this company."
					@row-click="openSubmission"
				>
					<template #cell-status="{ row }">
						<StatusBadge :label="row.status" :tone="governmentSubmissionTone(row.status)" />
					</template>
					<template #cell-outcome="{ row }">{{ row.outcome || '—' }}</template>
					<template #cell-generated_on="{ row }">{{ row.generated_on || '—' }}</template>
					<template #cell-submitted_on="{ row }">{{ row.submitted_on || '—' }}</template>
				</DataTable>
			</SectionCard>
		</div>
	</div>
</template>
