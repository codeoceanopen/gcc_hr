<script setup lang="ts">
import { computed, ref } from 'vue'
import { createDocumentResource, createListResource, call, toast, Button } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import Breadcrumbs from '@/components/ui/Breadcrumbs.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import Tabs from '@/components/ui/Tabs.vue'
import ComplianceScore from '@/components/ui/ComplianceScore.vue'
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable.vue'
import SaudiProfileCard from '@/components/employees/SaudiProfileCard.vue'
import QatarProfileCard from '@/components/employees/QatarProfileCard.vue'
import UAEProfileCard from '@/components/employees/UAEProfileCard.vue'
import OmanProfileCard from '@/components/employees/OmanProfileCard.vue'
import BahrainProfileCard from '@/components/employees/BahrainProfileCard.vue'
import KuwaitProfileCard from '@/components/employees/KuwaitProfileCard.vue'
import { documentStatusTone } from '@/utils/format'

const props = defineProps({ employee: { type: String, required: true } })

const profile = createDocumentResource({
	doctype: 'Employee Compliance Profile',
	name: props.employee,
	auto: true,
})

const documents = createListResource({
	doctype: 'HR Compliance Document',
	filters: { employee: props.employee },
	fields: ['name', 'document_type', 'document_number', 'expiry_date', 'status', 'days_remaining'],
	orderBy: 'expiry_date asc',
	pageLength: 50,
	auto: true,
})

const checks = createListResource({
	doctype: 'HR Compliance Check',
	filters: { employee: props.employee },
	fields: ['name', 'check_date', 'compliance_score', 'status', 'passed_rules', 'warnings', 'critical_issues'],
	orderBy: 'check_date desc',
	pageLength: 10,
	auto: true,
})

const latestCheck = computed(() => checks.data?.[0])

async function runComplianceCheck() {
	try {
		await call('gcc_hr.api.compliance.run_compliance_check_for_employee', { employee: props.employee })
		toast.success('Compliance check completed.')
		profile.reload()
		checks.reload()
	} catch {
		toast.error('Could not run compliance check.')
	}
}

const COUNTRY_TAB: Record<string, string> = {
	'Saudi Arabia': 'saudi',
	Qatar: 'qatar',
	'United Arab Emirates': 'uae',
	Oman: 'oman',
	Bahrain: 'bahrain',
	Kuwait: 'kuwait',
}

const activeTab = ref('overview')
const tabs = computed(() => {
	const base = [
		{ key: 'overview', label: 'Overview' },
		{ key: 'documents', label: 'Documents' },
		{ key: 'compliance', label: 'Compliance' },
	]
	const country = profile.doc?.country
	if (country && COUNTRY_TAB[country]) {
		base.push({ key: COUNTRY_TAB[country], label: country })
	}
	return base
})

const DOCUMENT_COLUMNS: DataTableColumn[] = [
	{ key: 'document_type', label: 'Document Type' },
	{ key: 'document_number', label: 'Number' },
	{ key: 'expiry_date', label: 'Expiry' },
	{ key: 'status', label: 'Status' },
]

const CHECK_COLUMNS: DataTableColumn[] = [
	{ key: 'check_date', label: 'Date' },
	{ key: 'compliance_score', label: 'Score', align: 'right' },
	{ key: 'passed_rules', label: 'Passed', align: 'right' },
	{ key: 'warnings', label: 'Warnings', align: 'right' },
	{ key: 'critical_issues', label: 'Critical', align: 'right' },
]
</script>

<template>
	<div v-if="profile.doc">
		<Breadcrumbs :items="[{ label: 'HR' }, { label: 'Employees', route: '/employees' }, { label: profile.doc.employee_name }]" />
		<PageHeader :title="profile.doc.employee_name" :description="`${profile.doc.designation || profile.doc.employment_type || ''} · ${profile.doc.company || ''}`">
			<template #action>
				<Button theme="blue" variant="solid" @click="runComplianceCheck">Run Compliance Check</Button>
			</template>
		</PageHeader>

		<div class="p-6">
			<SectionCard class="mb-4">
				<ComplianceScore :score="profile.doc.compliance_score" :status="profile.doc.compliance_status" />
			</SectionCard>

			<SectionCard no-padding>
				<Tabs v-model="activeTab" :tabs="tabs" />

				<div class="p-4">
					<div v-if="activeTab === 'overview'" class="grid grid-cols-1 gap-x-8 gap-y-3 sm:grid-cols-2">
						<div class="flex justify-between border-b border-app-border py-2 text-[13px]">
							<dt class="text-app-muted">Nationality</dt>
							<dd class="font-medium text-app-text">{{ profile.doc.nationality || '—' }}</dd>
						</div>
						<div class="flex justify-between border-b border-app-border py-2 text-[13px]">
							<dt class="text-app-muted">Country</dt>
							<dd class="font-medium text-app-text">{{ profile.doc.country || '—' }}</dd>
						</div>
						<div class="flex justify-between border-b border-app-border py-2 text-[13px]">
							<dt class="text-app-muted">Employment Type</dt>
							<dd class="font-medium text-app-text">{{ profile.doc.employment_type || '—' }}</dd>
						</div>
						<div class="flex justify-between border-b border-app-border py-2 text-[13px]">
							<dt class="text-app-muted">Joining Date</dt>
							<dd class="font-medium text-app-text">{{ profile.doc.joining_date || '—' }}</dd>
						</div>
						<div class="flex justify-between border-b border-app-border py-2 text-[13px]">
							<dt class="text-app-muted">Total Salary</dt>
							<dd class="font-medium text-app-text">{{ profile.doc.total_salary || '—' }}</dd>
						</div>
						<div class="flex justify-between border-b border-app-border py-2 text-[13px]">
							<dt class="text-app-muted">Last Checked</dt>
							<dd class="font-medium text-app-text">{{ profile.doc.last_compliance_check || '—' }}</dd>
						</div>
					</div>

					<DataTable
						v-else-if="activeTab === 'documents'"
						:columns="DOCUMENT_COLUMNS"
						:rows="documents.data || []"
						:loading="documents.loading"
						empty-title="No compliance documents on file"
					>
						<template #cell-status="{ row }">
							<StatusBadge :label="row.status" :tone="documentStatusTone(row.status)" />
						</template>
					</DataTable>

					<div v-else-if="activeTab === 'compliance'">
						<p v-if="!latestCheck" class="py-6 text-center text-[13px] text-app-muted">
							No compliance check has run for this employee yet.
						</p>
						<DataTable v-else :columns="CHECK_COLUMNS" :rows="checks.data || []" empty-title="No checks" />
					</div>

					<SaudiProfileCard v-else-if="activeTab === 'saudi'" :employee="employee" />
					<QatarProfileCard v-else-if="activeTab === 'qatar'" :employee="employee" />
					<UAEProfileCard v-else-if="activeTab === 'uae'" :employee="employee" />
					<OmanProfileCard v-else-if="activeTab === 'oman'" :employee="employee" />
					<BahrainProfileCard v-else-if="activeTab === 'bahrain'" :employee="employee" />
					<KuwaitProfileCard v-else-if="activeTab === 'kuwait'" :employee="employee" />
				</div>
			</SectionCard>
		</div>
	</div>
</template>
