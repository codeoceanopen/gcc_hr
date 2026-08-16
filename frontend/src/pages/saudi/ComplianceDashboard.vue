<script setup lang="ts">
import { computed, watch } from 'vue'
import { createDocumentResource, createResource } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import KpiCard from '@/components/ui/KpiCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import { Check, AlertTriangle } from 'lucide-vue-next'
import { useCompanyStore } from '@/stores/company'
import CompanySwitcher from '@/components/ui/CompanySwitcher.vue'

const companyStore = useCompanyStore()

// Saudization Profile is autonamed by company, so a document resource (not a
// list) is the right fetch -- same as CountryMetrics.vue's Saudi panel.
// createDocumentResource silently returns undefined if `name` is falsy at
// creation time (documentResource.js:15) -- companyStore.selectedCompany may
// still be '' here since the store's bootstrap() fetch is async, so a
// placeholder keeps the resource object alive until the watcher below sets
// the real name (auto:false means the placeholder is never actually fetched).
const profile = createDocumentResource({
	doctype: 'Saudization Profile',
	name: companyStore.selectedCompany || '__pending__',
	auto: false,
})

const summary = createResource({
	url: 'gcc_hr.api.dashboard.get_summary',
	params: { company: companyStore.selectedCompany },
	auto: false,
})

const PAYROLL_CHECK_FIELDS = ['name', 'status', 'total_employees', 'passed', 'warnings', 'critical', 'check_date']

const latestPayrollCheck = createResource({
	url: 'frappe.client.get_list',
	params: {
		doctype: 'Payroll Compliance Check',
		fields: PAYROLL_CHECK_FIELDS,
		filters: {},
		order_by: 'check_date desc',
		limit_page_length: 1,
	},
	auto: false,
})

watch(
	() => [companyStore.selectedCompany, companyStore.selectedCountry] as const,
	([company, country]) => {
		if (!company || country !== 'Saudi Arabia') return
		profile.name = company
		profile.reload()
		summary.update({ params: { company } })
		summary.reload()
		latestPayrollCheck.update({
			params: {
				doctype: 'Payroll Compliance Check',
				fields: PAYROLL_CHECK_FIELDS,
				filters: { company },
				order_by: 'check_date desc',
				limit_page_length: 1,
			},
		})
		latestPayrollCheck.reload()
	},
	{ immediate: true },
)

const latestCheck = computed(() => latestPayrollCheck.data?.[0])

function scoreTone(score: number): 'success' | 'warning' | 'danger' {
	if (score >= 75) return 'success'
	if (score >= 50) return 'warning'
	return 'danger'
}
</script>

<template>
	<div>
		<Breadcrumbs :items="[{ label: 'Saudi Arabia' }, { label: 'Compliance Dashboard' }]" />
		<PageHeader
			title="Saudi Arabia — HR Compliance"
			description="Saudization, document expiry, and payroll compliance for the selected company."
		>
			<template #action>
				<CompanySwitcher />
			</template>
		</PageHeader>

		<div class="space-y-4 p-6">
			<div v-if="companyStore.selectedCountry !== 'Saudi Arabia'" class="py-12 text-center text-[13px] text-app-muted">
				Select a Saudi Arabia company from the header to view this dashboard.
			</div>

			<LoadingState v-else-if="!profile.doc && (profile.loading || summary.loading)" />

			<template v-else-if="profile.doc">
				<div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
					<KpiCard label="Employees" :value="profile.doc.employee_count" />
					<KpiCard
						label="Saudization"
						:value="`${profile.doc.saudi_percentage}%`"
						:tone="profile.doc.compliance_status === 'Compliant' ? 'success' : profile.doc.compliance_status === 'At Risk' ? 'warning' : 'danger'"
						:hint="profile.doc.compliance_status"
					/>
					<KpiCard
						v-if="summary.data"
						label="Compliance"
						:value="`${summary.data.average_score}%`"
						:tone="scoreTone(summary.data.average_score)"
					/>
				</div>

				<SectionCard title="Saudi Workforce">
					<div class="grid grid-cols-2 gap-x-8 gap-y-2 text-[13px] sm:grid-cols-4">
						<div class="flex flex-col gap-0.5">
							<span class="text-app-muted">Saudi Employees</span>
							<span class="text-[16px] font-semibold leading-[20px] text-app-text">{{ profile.doc.saudi_employee_count }}</span>
						</div>
						<div class="flex flex-col gap-0.5">
							<span class="text-app-muted">Non-Saudi Employees</span>
							<span class="text-[16px] font-semibold leading-[20px] text-app-text">{{ profile.doc.non_saudi_employee_count }}</span>
						</div>
						<div class="flex flex-col gap-0.5">
							<span class="text-app-muted">Target</span>
							<span class="text-[16px] font-semibold leading-[20px] text-app-text">{{ profile.doc.target_percentage }}%</span>
						</div>
						<div class="flex flex-col gap-0.5">
							<span class="text-app-muted">Status</span>
							<StatusBadge
								:label="profile.doc.compliance_status"
								:tone="profile.doc.compliance_status === 'Compliant' ? 'success' : profile.doc.compliance_status === 'At Risk' ? 'warning' : 'danger'"
							/>
						</div>
					</div>
				</SectionCard>

				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<SectionCard title="Documents Expiring">
						<div v-if="!summary.data?.documents_expiring_by_type?.length" class="text-[13px] text-app-muted">
							Nothing expiring soon for this company.
						</div>
						<div v-else class="space-y-2">
							<div
								v-for="row in summary.data.documents_expiring_by_type"
								:key="row.document_type"
								class="flex items-center justify-between text-[13px]"
							>
								<span class="text-app-text">{{ row.document_type }}</span>
								<span class="font-medium text-app-warning">{{ row.count }}</span>
							</div>
						</div>
					</SectionCard>

					<SectionCard title="Payroll Compliance">
						<div v-if="!latestCheck" class="text-[13px] text-app-muted">
							No Payroll Compliance Check has run for this company yet.
						</div>
						<div v-else class="space-y-2 text-[13px]">
							<div class="flex items-center gap-2">
								<Check v-if="latestCheck.status === 'Passed'" :size="16" class="text-app-success" />
								<AlertTriangle v-else :size="16" class="text-app-warning" />
								<span class="text-app-text">Latest run: {{ latestCheck.status }} ({{ latestCheck.check_date }})</span>
							</div>
							<div class="flex items-center justify-between border-t border-app-border pt-2">
								<span class="text-app-muted">Passed</span>
								<span class="font-medium text-app-success">{{ latestCheck.passed }}</span>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-app-muted">Warnings</span>
								<span class="font-medium text-app-warning">{{ latestCheck.warnings }}</span>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-app-muted">Critical</span>
								<span class="font-medium text-app-danger">{{ latestCheck.critical }}</span>
							</div>
						</div>
					</SectionCard>
				</div>
			</template>

			<div v-else class="py-12 text-center text-[13px] text-app-muted">
				No Saudization Profile found yet -- run Recalculate on the Saudization page first.
			</div>
		</div>
	</div>
</template>
