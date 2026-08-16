<script setup lang="ts">
import { createDocumentResource } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { complianceTone } from '@/utils/format'

const props = defineProps<{ name: string }>()

const check = createDocumentResource({
	doctype: 'Payroll Compliance Check',
	name: props.name,
	auto: true,
})

function statusTone(status: string) {
	return status === 'Passed' ? 'success' : status === 'Warnings' ? 'warning' : 'danger'
}
</script>

<template>
	<div v-if="check.doc">
		<PageHeader
			:title="`Payroll Compliance -- ${check.doc.payroll_entry}`"
			:description="`${check.doc.company} · ${check.doc.check_date}`"
		/>

		<div class="p-6">
			<div class="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Status</p>
					<StatusBadge :label="check.doc.status" :tone="statusTone(check.doc.status)" />
				</div>
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Employees</p>
					<p class="mt-1 text-2xl font-semibold text-gray-900">{{ check.doc.total_employees }}</p>
				</div>
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Warnings</p>
					<p class="mt-1 text-2xl font-semibold text-gray-900">{{ check.doc.warnings }}</p>
				</div>
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Critical</p>
					<p class="mt-1 text-2xl font-semibold text-gray-900">{{ check.doc.critical }}</p>
				</div>
			</div>

			<div class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Employee</th>
							<th class="px-4 py-2 font-medium">Status</th>
							<th class="px-4 py-2 font-medium">Critical Issues</th>
							<th class="px-4 py-2 font-medium">Compliance Check</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="row in check.doc.employees" :key="row.name">
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ row.employee_name }}</td>
							<td class="px-4 py-2.5"><StatusBadge :label="row.status" :tone="complianceTone(row.status)" /></td>
							<td class="px-4 py-2.5 text-gray-600">{{ row.critical_issues }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ row.compliance_check }}</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</div>
</template>
