<script setup lang="ts">
import { createListResource, call } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const countries = createListResource({
	doctype: 'HR Country Settings',
	fields: ['name', 'country', 'currency', 'is_active', 'compliance_engine_enabled', 'government_integration_enabled'],
	orderBy: 'country asc',
	pageLength: 20,
	auto: true,
})

type ToggleField = 'is_active' | 'compliance_engine_enabled'

async function toggle(row: Record<string, any>, fieldname: ToggleField) {
	const value = row[fieldname] ? 0 : 1
	await call('frappe.client.set_value', { doctype: 'HR Country Settings', name: row.name, fieldname, value })
	row[fieldname] = value
}
</script>

<template>
	<div>
		<PageHeader
			title="Country Settings"
			description="Which GCC countries are active, and whether their compliance engine / government integration is enabled."
		/>

		<div class="p-6">
			<div v-if="countries.loading && !countries.data" class="text-sm text-gray-500">Loading...</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Country</th>
							<th class="px-4 py-2 font-medium">Currency</th>
							<th class="px-4 py-2 font-medium">Active</th>
							<th class="px-4 py-2 font-medium">Compliance Engine</th>
							<th class="px-4 py-2 font-medium">Government Integration</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr v-for="c in countries.data" :key="c.name">
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ c.country }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ c.currency }}</td>
							<td class="px-4 py-2.5">
								<button
									class="rounded px-2 py-0.5 text-xs"
									:class="c.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
									@click="toggle(c, 'is_active')"
								>
									{{ c.is_active ? 'Active' : 'Inactive' }}
								</button>
							</td>
							<td class="px-4 py-2.5">
								<button
									class="rounded px-2 py-0.5 text-xs"
									:class="c.compliance_engine_enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
									@click="toggle(c, 'compliance_engine_enabled')"
								>
									{{ c.compliance_engine_enabled ? 'Enabled' : 'Disabled' }}
								</button>
							</td>
							<td class="px-4 py-2.5">
								<StatusBadge
									:label="c.government_integration_enabled ? 'Enabled' : 'Not Available'"
									:tone="c.government_integration_enabled ? 'success' : 'neutral'"
								/>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
			<p class="mt-3 text-xs text-gray-400">
				Government integration for GCC countries is only enabled once a verified official API is available
				(see the Government Integration Framework, Phase 5) -- it can't be toggled from here.
			</p>
		</div>
	</div>
</template>
