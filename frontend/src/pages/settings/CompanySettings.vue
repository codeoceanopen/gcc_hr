<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createListResource, toast, Button, Dialog, FormControl } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'

const companies = createListResource({
	doctype: 'GCC HR Company Settings',
	fields: ['name', 'company', 'country', 'currency', 'compliance_enabled', 'payroll_frequency', 'government_integration_enabled'],
	orderBy: 'company asc',
	pageLength: 50,
	auto: true,
})

const dialogOpen = ref(false)
const form = reactive({ company: '', country: '' })

function openCreate() {
	form.company = ''
	form.country = ''
	dialogOpen.value = true
}

async function create() {
	if (!form.company || !form.country) {
		toast.error('Company and Country are required.')
		return
	}
	try {
		await companies.insert.submit({ ...form })
		toast.success('Company settings created.')
		dialogOpen.value = false
	} catch {
		toast.error('Could not create company settings -- check that this company is not already configured.')
	}
}
</script>

<template>
	<div>
		<PageHeader
			title="Company Settings"
			description="Country, payroll and government-integration configuration per company. Selecting a country activates that country's localization."
		>
			<template #action>
				<Button variant="solid" @click="openCreate">Configure Company</Button>
			</template>
		</PageHeader>

		<div class="p-6">
			<div v-if="companies.loading && !companies.data" class="text-sm text-gray-500">Loading...</div>
			<div v-else-if="!companies.data?.length" class="text-sm text-gray-500">
				No companies configured yet.
			</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Company</th>
							<th class="px-4 py-2 font-medium">Country</th>
							<th class="px-4 py-2 font-medium">Currency</th>
							<th class="px-4 py-2 font-medium">Payroll Frequency</th>
							<th class="px-4 py-2 font-medium">Compliance</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="c in companies.data" :key="c.name">
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ c.company }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.country }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.currency || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.payroll_frequency || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.compliance_enabled ? 'Enabled' : 'Disabled' }}</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<Dialog v-model="dialogOpen" :options="{ title: 'Configure Company' }">
			<template #body-content>
				<div class="space-y-4">
					<FormControl v-model="form.company" label="Company" type="text" required
						description="Must match an existing Company, e.g. glob" />
					<FormControl v-model="form.country" label="Country" type="text" required
						description="Must match an HR Country Settings record, e.g. Saudi Arabia" />
				</div>
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="companies.insert.loading" @click="create">Create</Button>
					<Button variant="outline" @click="dialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>
