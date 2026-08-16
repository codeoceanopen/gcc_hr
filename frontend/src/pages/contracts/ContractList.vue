<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createListResource, toast, Button, Dialog, FormControl } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const contracts = createListResource({
	doctype: 'Contract',
	filters: { party_type: 'Employee' },
	fields: [
		'name',
		'party_name',
		'status',
		'start_date',
		'end_date',
		'gcc_basic_salary',
		'gcc_total_salary',
		'docstatus',
	],
	orderBy: 'modified desc',
	pageLength: 100,
	auto: true,
})

const dialogOpen = ref(false)
const form = reactive({
	party_name: '',
	start_date: '',
	end_date: '',
	contract_terms: '',
	gcc_basic_salary: 0,
	gcc_housing_allowance: 0,
	gcc_transport_allowance: 0,
	gcc_other_allowances: 0,
})

function openCreate() {
	Object.assign(form, {
		party_name: '',
		start_date: '',
		end_date: '',
		contract_terms: '',
		gcc_basic_salary: 0,
		gcc_housing_allowance: 0,
		gcc_transport_allowance: 0,
		gcc_other_allowances: 0,
	})
	dialogOpen.value = true
}

async function create() {
	if (!form.party_name || !form.start_date || !form.contract_terms) {
		toast.error('Employee, Start Date and Contract Terms are required.')
		return
	}
	try {
		await contracts.insert.submit({ party_type: 'Employee', ...form })
		toast.success('Contract created.')
		dialogOpen.value = false
	} catch {
		toast.error('Could not create contract.')
	}
}

function docstatusTone(docstatus: number) {
	return docstatus === 1 ? 'success' : docstatus === 2 ? 'danger' : 'neutral'
}

function docstatusLabel(docstatus: number) {
	return docstatus === 1 ? 'Submitted' : docstatus === 2 ? 'Cancelled' : 'Draft'
}
</script>

<template>
	<div>
		<PageHeader
			title="Employment Contracts"
			description="Extends the standard Contract doctype with GCC salary breakdown -- see the Employee Compliance Profile for the linked contract per employee."
		>
			<template #action>
				<Button variant="solid" @click="openCreate">New Contract</Button>
			</template>
		</PageHeader>

		<div class="p-6">
			<div v-if="contracts.loading && !contracts.data" class="text-sm text-gray-500">Loading...</div>
			<div v-else-if="!contracts.data?.length" class="text-sm text-gray-500">No employment contracts yet.</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Employee</th>
							<th class="px-4 py-2 font-medium">Start</th>
							<th class="px-4 py-2 font-medium">End</th>
							<th class="px-4 py-2 font-medium">Basic Salary</th>
							<th class="px-4 py-2 font-medium">Total Salary</th>
							<th class="px-4 py-2 font-medium">Status</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="c in contracts.data" :key="c.name">
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ c.party_name }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.start_date || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.end_date || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.gcc_basic_salary || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.gcc_total_salary || '—' }}</td>
							<td class="px-4 py-2.5">
								<StatusBadge :label="docstatusLabel(c.docstatus)" :tone="docstatusTone(c.docstatus)" />
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<Dialog v-model="dialogOpen" :options="{ title: 'New Employment Contract' }">
			<template #body-content>
				<div class="space-y-4">
					<FormControl v-model="form.party_name" label="Employee" type="text" required
						description="Employee ID, e.g. HR-EMP-00001" />
					<FormControl v-model="form.start_date" label="Start Date" type="date" required />
					<FormControl v-model="form.end_date" label="End Date" type="date" />
					<FormControl v-model="form.gcc_basic_salary" label="Basic Salary" type="number" />
					<FormControl v-model="form.gcc_housing_allowance" label="Housing Allowance" type="number" />
					<FormControl v-model="form.gcc_transport_allowance" label="Transport Allowance" type="number" />
					<FormControl v-model="form.gcc_other_allowances" label="Other Allowances" type="number" />
					<FormControl v-model="form.contract_terms" label="Contract Terms" type="textarea" required />
				</div>
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="contracts.insert.loading" @click="create">Create</Button>
					<Button variant="outline" @click="dialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>
