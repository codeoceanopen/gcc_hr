<script setup lang="ts">
import { createListResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const router = useRouter()

const checks = createListResource({
	doctype: 'Payroll Compliance Check',
	fields: ['name', 'payroll_entry', 'company', 'check_date', 'total_employees', 'passed', 'warnings', 'critical', 'status'],
	orderBy: 'check_date desc',
	pageLength: 50,
	auto: true,
})

function statusTone(status: string) {
	return status === 'Passed' ? 'success' : status === 'Warnings' ? 'warning' : 'danger'
}
</script>

<template>
	<div>
		<PageHeader
			title="Payroll Compliance"
			description="Runs automatically before every Payroll Entry submission -- one row per run, with a per-employee breakdown. Blocking behaviour is controlled by GCC HR Company Settings' Payroll Compliance Required."
		/>

		<div class="p-6">
			<div v-if="checks.loading && !checks.data" class="text-sm text-gray-500">Loading...</div>
			<div v-else-if="!checks.data?.length" class="text-sm text-gray-500">
				No payroll compliance checks yet -- these are created automatically when a Payroll Entry is submitted.
			</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Payroll Entry</th>
							<th class="px-4 py-2 font-medium">Company</th>
							<th class="px-4 py-2 font-medium">Check Date</th>
							<th class="px-4 py-2 font-medium">Employees</th>
							<th class="px-4 py-2 font-medium">Passed</th>
							<th class="px-4 py-2 font-medium">Warnings</th>
							<th class="px-4 py-2 font-medium">Critical</th>
							<th class="px-4 py-2 font-medium">Status</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr
							v-for="c in checks.data"
							:key="c.name"
							class="cursor-pointer hover:bg-gray-50"
							@click="router.push(`/payroll/${c.name}`)"
						>
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ c.payroll_entry }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.company }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.check_date }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.total_employees }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.passed }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.warnings }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.critical }}</td>
							<td class="px-4 py-2.5"><StatusBadge :label="c.status" :tone="statusTone(c.status)" /></td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</div>
</template>
