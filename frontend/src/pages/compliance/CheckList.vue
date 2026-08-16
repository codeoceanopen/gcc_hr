<script setup lang="ts">
import { createListResource } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { complianceTone } from '@/utils/format'

const checks = createListResource({
	doctype: 'HR Compliance Check',
	fields: [
		'name', 'employee_name', 'check_date', 'compliance_score', 'status', 'passed_rules', 'warnings', 'critical_issues',
	],
	orderBy: 'check_date desc',
	pageLength: 100,
	auto: true,
})
</script>

<template>
	<div>
		<PageHeader
			title="Compliance Checks"
			description="History of compliance engine runs. Checks are created by the system (scheduled or manual), never edited by hand."
		/>

		<div class="p-6">
			<div v-if="checks.loading && !checks.data" class="text-sm text-gray-500">Loading...</div>
			<div v-else-if="!checks.data?.length" class="text-sm text-gray-500">
				No compliance checks have run yet.
			</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Employee</th>
							<th class="px-4 py-2 font-medium">Check Date</th>
							<th class="px-4 py-2 font-medium">Score</th>
							<th class="px-4 py-2 font-medium">Status</th>
							<th class="px-4 py-2 font-medium">Passed</th>
							<th class="px-4 py-2 font-medium">Warnings</th>
							<th class="px-4 py-2 font-medium">Critical</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="c in checks.data" :key="c.name">
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ c.employee_name }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.check_date }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.compliance_score }}%</td>
							<td class="px-4 py-2.5"><StatusBadge :label="c.status" :tone="complianceTone(c.status)" /></td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.passed_rules }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.warnings }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.critical_issues }}</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</div>
</template>
