<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createListResource, toast, Button, Dialog, FormControl } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { documentStatusTone } from '@/utils/format'

const documents = createListResource({
	doctype: 'HR Compliance Document',
	fields: ['name', 'employee', 'employee_name', 'document_type', 'document_number', 'expiry_date', 'status', 'days_remaining'],
	orderBy: 'expiry_date asc',
	pageLength: 100,
	auto: true,
})

const dialogOpen = ref(false)
const form = reactive({ employee: '', document_type: '', document_number: '', issue_date: '', expiry_date: '' })

function openCreate() {
	form.employee = ''
	form.document_type = ''
	form.document_number = ''
	form.issue_date = ''
	form.expiry_date = ''
	dialogOpen.value = true
}

async function create() {
	if (!form.employee || !form.document_type) {
		toast.error('Employee and Document Type are required.')
		return
	}
	try {
		await documents.insert.submit({ ...form })
		toast.success('Compliance document created.')
		dialogOpen.value = false
	} catch {
		toast.error('Could not create compliance document.')
	}
}
</script>

<template>
	<div>
		<PageHeader title="Compliance Documents" description="Iqama, passport, work permit and other tracked documents, across all employees.">
			<template #action>
				<Button variant="solid" @click="openCreate">New Document</Button>
			</template>
		</PageHeader>

		<div class="p-6">
			<div v-if="documents.loading && !documents.data" class="text-sm text-gray-500">Loading...</div>

			<div v-else-if="!documents.data?.length" class="text-sm text-gray-500">No compliance documents yet.</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Employee</th>
							<th class="px-4 py-2 font-medium">Document Type</th>
							<th class="px-4 py-2 font-medium">Number</th>
							<th class="px-4 py-2 font-medium">Expiry</th>
							<th class="px-4 py-2 font-medium">Days Remaining</th>
							<th class="px-4 py-2 font-medium">Status</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="d in documents.data" :key="d.name">
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ d.employee_name }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ d.document_type }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ d.document_number || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ d.expiry_date || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ d.days_remaining ?? '—' }}</td>
							<td class="px-4 py-2.5">
								<StatusBadge :label="d.status" :tone="documentStatusTone(d.status)" />
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<Dialog v-model="dialogOpen" :options="{ title: 'New Compliance Document' }">
			<template #body-content>
				<div class="space-y-4">
					<FormControl v-model="form.employee" label="Employee" type="text" required
						description="Employee ID, e.g. HR-EMP-00001" />
					<FormControl v-model="form.document_type" label="Document Type" type="text" required
						description="e.g. Saudi Arabia-Iqama" />
					<FormControl v-model="form.document_number" label="Document Number" type="text" />
					<FormControl v-model="form.issue_date" label="Issue Date" type="date" />
					<FormControl v-model="form.expiry_date" label="Expiry Date" type="date" />
				</div>
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="documents.insert.loading" @click="create">Create</Button>
					<Button variant="outline" @click="dialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>
