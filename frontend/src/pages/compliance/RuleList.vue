<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createListResource, call, toast, Button, Dialog, FormControl } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { severityTone } from '@/utils/format'

const CATEGORIES = [
	'Employee', 'Document', 'Payroll', 'Contract', 'Government', 'Workforce', 'Nationality', 'Leave',
	'Attendance', 'Termination',
]
const SEVERITIES = ['Info', 'Warning', 'Critical', 'Blocking']

const rules = createListResource({
	doctype: 'HR Compliance Rule',
	fields: ['name', 'rule_code', 'rule_name', 'country', 'category', 'severity', 'enabled'],
	orderBy: 'country asc, severity desc',
	pageLength: 100,
	auto: true,
})

const dialogOpen = ref(false)
const form = reactive({
	rule_code: '', rule_name: '', country: '', category: 'Document', severity: 'Warning', check_method: '',
})

function openCreate() {
	Object.assign(form, {
		rule_code: '', rule_name: '', country: '', category: 'Document', severity: 'Warning', check_method: '',
	})
	dialogOpen.value = true
}

async function create() {
	if (!form.rule_code || !form.rule_name || !form.country || !form.check_method) {
		toast.error('Rule Code, Rule Name, Country and Check Method are required.')
		return
	}
	try {
		await rules.insert.submit({ ...form })
		toast.success('Compliance rule created.')
		dialogOpen.value = false
	} catch {
		toast.error('Could not create rule -- check that Rule Code is unique and Check Method is importable.')
	}
}

async function toggleEnabled(rule: { name: string; enabled: number }) {
	const enabled = rule.enabled ? 0 : 1
	await call('frappe.client.set_value', { doctype: 'HR Compliance Rule', name: rule.name, fieldname: 'enabled', value: enabled })
	rule.enabled = enabled
}
</script>

<template>
	<div>
		<PageHeader title="Compliance Rules" description="Configurable rules the compliance engine evaluates per country.">
			<template #action>
				<Button variant="solid" @click="openCreate">New Rule</Button>
			</template>
		</PageHeader>

		<div class="p-6">
			<div v-if="rules.loading && !rules.data" class="text-sm text-gray-500">Loading...</div>
			<div v-else-if="!rules.data?.length" class="text-sm text-gray-500">No compliance rules configured yet.</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Rule</th>
							<th class="px-4 py-2 font-medium">Country</th>
							<th class="px-4 py-2 font-medium">Category</th>
							<th class="px-4 py-2 font-medium">Severity</th>
							<th class="px-4 py-2 font-medium">Enabled</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="r in rules.data" :key="r.name">
							<td class="px-4 py-2.5">
								<p class="font-medium text-gray-900">{{ r.rule_name }}</p>
								<p class="text-xs text-gray-400">{{ r.rule_code }}</p>
							</td>
							<td class="px-4 py-2.5 text-gray-600">{{ r.country }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ r.category }}</td>
							<td class="px-4 py-2.5"><StatusBadge :label="r.severity" :tone="severityTone(r.severity)" /></td>
							<td class="px-4 py-2.5">
								<button
									class="rounded px-2 py-0.5 text-xs"
									:class="r.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
									@click="toggleEnabled(r)"
								>
									{{ r.enabled ? 'Enabled' : 'Disabled' }}
								</button>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<Dialog v-model="dialogOpen" :options="{ title: 'New Compliance Rule' }">
			<template #body-content>
				<div class="space-y-4">
					<FormControl v-model="form.rule_code" label="Rule Code" type="text" required
						description="e.g. IQAMA_EXPIRY" />
					<FormControl v-model="form.rule_name" label="Rule Name" type="text" required />
					<FormControl v-model="form.country" label="Country" type="text" required
						description="Must match an HR Country Settings record, e.g. Saudi Arabia" />
					<FormControl v-model="form.category" label="Category" type="select"
						:options="CATEGORIES" />
					<FormControl v-model="form.severity" label="Severity" type="select" :options="SEVERITIES" />
					<FormControl v-model="form.check_method" label="Check Method" type="text" required
						description="Dotted Python path to the check function" />
				</div>
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="rules.insert.loading" @click="create">Create</Button>
					<Button variant="outline" @click="dialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>
