<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createListResource, toast, Button, Dialog, FormControl } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const settings = createListResource({
	doctype: 'GOSI Settings',
	fields: [
		'name',
		'applicable_employee_category',
		'effective_from',
		'effective_to',
		'employee_contribution_rate',
		'employer_contribution_rate',
		'contribution_floor',
		'contribution_ceiling',
	],
	orderBy: 'effective_from desc',
	pageLength: 20,
	auto: true,
})

const profiles = createListResource({
	doctype: 'GOSI Employee Profile',
	fields: ['name', 'employee_name', 'registration_status', 'gosi_number', 'status'],
	orderBy: 'modified desc',
	pageLength: 50,
	auto: true,
})

const calculations = createListResource({
	doctype: 'GOSI Payroll Calculation',
	fields: [
		'name',
		'employee_name',
		'salary_slip',
		'contribution_base',
		'employee_contribution',
		'employer_contribution',
		'total_contribution',
		'calculation_date',
	],
	orderBy: 'calculation_date desc',
	pageLength: 20,
	auto: true,
})

const dialogOpen = ref(false)
const form = reactive({ employee: '', registration_status: 'Registered', gosi_number: '' })

function openCreate() {
	Object.assign(form, { employee: '', registration_status: 'Registered', gosi_number: '' })
	dialogOpen.value = true
}

async function create() {
	if (!form.employee) {
		toast.error('Employee is required.')
		return
	}
	try {
		await profiles.insert.submit({ ...form })
		toast.success('GOSI Employee Profile created.')
		dialogOpen.value = false
	} catch {
		toast.error('Could not create GOSI Employee Profile.')
	}
}

function registrationTone(status: string) {
	return status === 'Registered' ? 'success' : status === 'Pending' ? 'warning' : 'neutral'
}
</script>

<template>
	<div>
		<PageHeader
			title="GOSI"
			description="General Organization for Social Insurance -- registration status and contribution calculations. Rates are configuration (GOSI Settings), never hard-coded -- verify against the official circular before relying on them for real payroll."
		>
			<template #action>
				<Button variant="solid" @click="openCreate">New GOSI Employee Profile</Button>
			</template>
		</PageHeader>

		<div class="space-y-6 p-6">
			<div class="rounded-xl border bg-white p-4">
				<p class="mb-3 text-sm font-medium text-gray-700">GOSI Settings (effective-dated contribution rates)</p>
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-2 py-1.5 font-medium">Category</th>
							<th class="px-2 py-1.5 font-medium">Effective From</th>
							<th class="px-2 py-1.5 font-medium">Effective To</th>
							<th class="px-2 py-1.5 font-medium">Employee %</th>
							<th class="px-2 py-1.5 font-medium">Employer %</th>
							<th class="px-2 py-1.5 font-medium">Floor</th>
							<th class="px-2 py-1.5 font-medium">Ceiling</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="s in settings.data" :key="s.name">
							<td class="px-2 py-1.5 font-medium text-gray-900">{{ s.applicable_employee_category }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ s.effective_from }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ s.effective_to || 'open-ended' }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ s.employee_contribution_rate }}%</td>
							<td class="px-2 py-1.5 text-gray-600">{{ s.employer_contribution_rate }}%</td>
							<td class="px-2 py-1.5 text-gray-600">{{ s.contribution_floor }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ s.contribution_ceiling }}</td>
						</tr>
					</tbody>
				</table>
			</div>

			<div class="rounded-xl border bg-white p-4">
				<p class="mb-3 text-sm font-medium text-gray-700">Employee Registration</p>
				<div v-if="!profiles.data?.length" class="text-sm text-gray-500">No GOSI Employee Profiles yet.</div>
				<table v-else class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-2 py-1.5 font-medium">Employee</th>
							<th class="px-2 py-1.5 font-medium">GOSI Number</th>
							<th class="px-2 py-1.5 font-medium">Registration Status</th>
							<th class="px-2 py-1.5 font-medium">Contribution Status</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="p in profiles.data" :key="p.name">
							<td class="px-2 py-1.5 font-medium text-gray-900">{{ p.employee_name }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ p.gosi_number || '—' }}</td>
							<td class="px-2 py-1.5">
								<StatusBadge :label="p.registration_status" :tone="registrationTone(p.registration_status)" />
							</td>
							<td class="px-2 py-1.5 text-gray-600">{{ p.status }}</td>
						</tr>
					</tbody>
				</table>
			</div>

			<div class="rounded-xl border bg-white p-4">
				<p class="mb-3 text-sm font-medium text-gray-700">Recent Payroll Calculations</p>
				<div v-if="!calculations.data?.length" class="text-sm text-gray-500">
					No GOSI contributions calculated yet -- these are created automatically when a registered employee's
					Salary Slip is submitted.
				</div>
				<table v-else class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-2 py-1.5 font-medium">Employee</th>
							<th class="px-2 py-1.5 font-medium">Salary Slip</th>
							<th class="px-2 py-1.5 font-medium">Contribution Base</th>
							<th class="px-2 py-1.5 font-medium">Employee</th>
							<th class="px-2 py-1.5 font-medium">Employer</th>
							<th class="px-2 py-1.5 font-medium">Total</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="c in calculations.data" :key="c.name">
							<td class="px-2 py-1.5 font-medium text-gray-900">{{ c.employee_name }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ c.salary_slip }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ c.contribution_base }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ c.employee_contribution }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ c.employer_contribution }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ c.total_contribution }}</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<Dialog v-model="dialogOpen" :options="{ title: 'New GOSI Employee Profile' }">
			<template #body-content>
				<div class="space-y-4">
					<FormControl v-model="form.employee" label="Employee" type="text" required
						description="Employee ID, e.g. HR-EMP-00001" />
					<FormControl
						v-model="form.registration_status"
						label="Registration Status"
						type="select"
						:options="['Not Registered', 'Pending', 'Registered']"
					/>
					<FormControl v-model="form.gosi_number" label="GOSI Number" type="text" />
				</div>
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="profiles.insert.loading" @click="create">Create</Button>
					<Button variant="outline" @click="dialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>
