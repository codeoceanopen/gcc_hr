<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createListResource, call, toast, Button, FormControl } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const profiles = createListResource({
	doctype: 'Qatarization Profile',
	fields: [
		'name',
		'company',
		'activity',
		'business_size',
		'employee_count',
		'qatari_employee_count',
		'non_qatari_employee_count',
		'qatari_percentage',
		'target_percentage',
		'gap',
		'compliance_status',
		'last_calculation',
	],
	orderBy: 'qatari_percentage asc',
	pageLength: 50,
	auto: true,
})

const recalculating = ref<string | null>(null)
async function recalculate(company: string) {
	recalculating.value = company
	try {
		await call('gcc_hr.api.qatarization.recalculate_now', { company })
		toast.success(`Recalculated Qatarization for ${company}.`)
		profiles.reload()
	} catch {
		toast.error('Could not recalculate.')
	} finally {
		recalculating.value = null
	}
}

function statusTone(status: string) {
	return status === 'Compliant' ? 'success' : status === 'At Risk' ? 'warning' : 'danger'
}

// What-If Simulator
const simForm = reactive({
	company: '',
	hire_qatari: 0,
	hire_non_qatari: 0,
	terminate_qatari: 0,
	terminate_non_qatari: 0,
})
const simResult = ref<any>(null)
const simLoading = ref(false)

async function runSimulation() {
	if (!simForm.company) {
		toast.error('Pick a company to simulate.')
		return
	}
	simLoading.value = true
	try {
		simResult.value = await call('gcc_hr.api.qatarization.simulate', { ...simForm })
	} catch {
		toast.error('Could not run simulation.')
	} finally {
		simLoading.value = false
	}
}
</script>

<template>
	<div>
		<PageHeader
			title="Qatarization"
			description="Workforce-nationalization tracking for Qatar. Target percentages are configuration (Qatarization Requirement) -- never one universal number -- and the What-If Simulator never touches real employee data."
		/>

		<div class="space-y-6 p-6">
			<div class="rounded-xl border bg-white p-4">
				<p class="mb-3 text-sm font-medium text-gray-700">Company Qatarization Status</p>
				<div v-if="!profiles.data?.length" class="text-sm text-gray-500">
					No Qatarization Profiles yet -- these are created automatically when a company's country is set to
					Qatar, and recalculated daily.
				</div>
				<table v-else class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-2 py-1.5 font-medium">Company</th>
							<th class="px-2 py-1.5 font-medium">Employees</th>
							<th class="px-2 py-1.5 font-medium">Qatari</th>
							<th class="px-2 py-1.5 font-medium">Non-Qatari</th>
							<th class="px-2 py-1.5 font-medium">Qatari %</th>
							<th class="px-2 py-1.5 font-medium">Target %</th>
							<th class="px-2 py-1.5 font-medium">Gap</th>
							<th class="px-2 py-1.5 font-medium">Status</th>
							<th class="px-2 py-1.5 font-medium"></th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="p in profiles.data" :key="p.name">
							<td class="px-2 py-1.5 font-medium text-gray-900">{{ p.company }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ p.employee_count }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ p.qatari_employee_count }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ p.non_qatari_employee_count }}</td>
							<td class="px-2 py-1.5 text-gray-600">{{ p.qatari_percentage }}%</td>
							<td class="px-2 py-1.5 text-gray-600">{{ p.target_percentage }}%</td>
							<td class="px-2 py-1.5" :class="p.gap < 0 ? 'text-red-600' : 'text-green-600'">{{ p.gap }}%</td>
							<td class="px-2 py-1.5"><StatusBadge :label="p.compliance_status" :tone="statusTone(p.compliance_status)" /></td>
							<td class="px-2 py-1.5">
								<Button
									variant="outline"
									:loading="recalculating === p.company"
									@click="recalculate(p.company)"
								>
									Recalculate
								</Button>
							</td>
						</tr>
					</tbody>
				</table>
			</div>

			<div class="rounded-xl border bg-white p-4">
				<p class="mb-1 text-sm font-medium text-gray-700">What-If Simulator</p>
				<p class="mb-3 text-xs text-gray-500">
					Projects the effect of hiring/terminating employees without changing any real data.
				</p>
				<div class="grid grid-cols-2 gap-3 sm:grid-cols-5">
					<FormControl v-model="simForm.company" label="Company" type="text" description="e.g. glob" />
					<FormControl v-model="simForm.hire_qatari" label="Hire Qatari" type="number" />
					<FormControl v-model="simForm.hire_non_qatari" label="Hire Non-Qatari" type="number" />
					<FormControl v-model="simForm.terminate_qatari" label="Terminate Qatari" type="number" />
					<FormControl v-model="simForm.terminate_non_qatari" label="Terminate Non-Qatari" type="number" />
				</div>
				<div class="mt-4">
					<Button variant="solid" :loading="simLoading" @click="runSimulation">Simulate</Button>
				</div>

				<div v-if="simResult" class="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
					<div class="rounded-lg border p-3">
						<p class="text-xs uppercase tracking-wide text-gray-400">Current %</p>
						<p class="mt-1 text-xl font-semibold text-gray-900">{{ simResult.current_percentage }}%</p>
					</div>
					<div class="rounded-lg border p-3">
						<p class="text-xs uppercase tracking-wide text-gray-400">Projected %</p>
						<p class="mt-1 text-xl font-semibold text-gray-900">{{ simResult.projected_percentage }}%</p>
					</div>
					<div class="rounded-lg border p-3">
						<p class="text-xs uppercase tracking-wide text-gray-400">Target %</p>
						<p class="mt-1 text-xl font-semibold text-gray-900">{{ simResult.target_percentage ?? '—' }}%</p>
					</div>
					<div class="rounded-lg border p-3">
						<p class="text-xs uppercase tracking-wide text-gray-400">Projected Risk</p>
						<StatusBadge :label="simResult.projected_status" :tone="statusTone(simResult.projected_status)" />
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
