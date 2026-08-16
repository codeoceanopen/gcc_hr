<script setup lang="ts">
import { computed, watch } from 'vue'
import { createDocumentResource, createResource } from 'frappe-ui'
import SectionCard from './SectionCard.vue'
import KpiCard from './KpiCard.vue'
import StatusBadge from './StatusBadge.vue'
import EmptyState from './EmptyState.vue'

const props = defineProps<{
	company: string
	country: string
}>()

// Only Saudi Arabia has a real per-country metrics panel today -- for every
// other country this deliberately renders nothing rather than a fake/
// placeholder panel (spec: "don't show irrelevant/empty country data").
const isSaudi = computed(() => props.country === 'Saudi Arabia')

// createDocumentResource silently returns undefined if `name` is falsy at
// creation time (documentResource.js:15) -- props.company may still be ''
// when this mounts, so a placeholder keeps the resource alive until the
// watcher below sets the real name (auto:false means it's never fetched).
const saudization = createDocumentResource({
	doctype: 'Saudization Profile',
	name: props.company || '__pending__',
	auto: false,
})

const gosiSummary = createResource({
	url: 'gcc_hr.api.saudization.get_gosi_summary',
	params: { company: props.company },
	auto: false,
})

watch(
	() => [props.company, isSaudi.value] as const,
	([company, saudi]) => {
		if (!company || !saudi) return
		saudization.name = company
		saudization.reload()
		gosiSummary.update({ params: { company } })
		gosiSummary.reload()
	},
	{ immediate: true },
)

function statusTone(status: string): 'success' | 'warning' | 'danger' {
	if (status === 'Compliant') return 'success'
	if (status === 'At Risk') return 'warning'
	return 'danger'
}
</script>

<template>
	<template v-if="isSaudi">
		<SectionCard title="Saudi Arabia — Key Metrics">
			<div v-if="!saudization.doc" class="py-6">
				<EmptyState
					title="No Saudization Profile yet"
					description="Run Recalculate on the Saudization page to compute this company's metrics."
				/>
			</div>
			<div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3">
				<KpiCard label="Saudi Employees" :value="saudization.doc.saudi_employee_count" />
				<KpiCard
					label="Saudization"
					:value="`${saudization.doc.saudi_percentage}%`"
					:tone="statusTone(saudization.doc.compliance_status)"
					:hint="saudization.doc.compliance_status"
				/>
				<KpiCard
					v-if="gosiSummary.data"
					label="GOSI Status"
					:value="gosiSummary.data.status"
					:tone="gosiSummary.data.status === 'Compliant' ? 'success' : 'warning'"
					:hint="gosiSummary.data.needs_review ? `${gosiSummary.data.needs_review} need review` : undefined"
				/>
			</div>
		</SectionCard>

		<div v-if="saudization.doc" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
			<SectionCard title="Saudization Overview" no-padding>
				<table class="w-full text-[13px]">
					<thead>
						<tr class="border-b border-app-border text-left text-[11px] uppercase tracking-wide text-app-muted">
							<th class="px-4 py-2 font-medium">Description</th>
							<th class="px-4 py-2 text-right font-medium">Count</th>
							<th class="px-4 py-2 text-right font-medium">Percentage</th>
						</tr>
					</thead>
					<tbody>
						<tr class="border-b border-app-border">
							<td class="px-4 py-2 text-app-text">Saudi Employees</td>
							<td class="px-4 py-2 text-right text-app-text">{{ saudization.doc.saudi_employee_count }}</td>
							<td class="px-4 py-2 text-right text-app-text">{{ saudization.doc.saudi_percentage }}%</td>
						</tr>
						<tr class="border-b border-app-border">
							<td class="px-4 py-2 text-app-text">Non-Saudi Employees</td>
							<td class="px-4 py-2 text-right text-app-text">{{ saudization.doc.non_saudi_employee_count }}</td>
							<td class="px-4 py-2 text-right text-app-text">
								{{ Math.round((100 - saudization.doc.saudi_percentage) * 10) / 10 }}%
							</td>
						</tr>
						<tr>
							<td class="px-4 py-2 font-medium text-app-text">Total Employees</td>
							<td class="px-4 py-2 text-right font-medium text-app-text">{{ saudization.doc.employee_count }}</td>
							<td class="px-4 py-2 text-right font-medium text-app-text">100%</td>
						</tr>
					</tbody>
				</table>
			</SectionCard>

			<SectionCard title="GOSI">
				<div v-if="!gosiSummary.data" class="py-6 text-center text-[13px] text-app-muted">Loading...</div>
				<div v-else class="space-y-2 text-[13px]">
					<div class="flex items-center justify-between">
						<span class="text-app-muted">Status</span>
						<StatusBadge :label="gosiSummary.data.status" :tone="gosiSummary.data.status === 'Compliant' ? 'success' : 'warning'" />
					</div>
					<div class="flex items-center justify-between border-t border-app-border pt-2">
						<span class="text-app-muted">Registered</span>
						<span class="font-medium text-app-success">{{ gosiSummary.data.counts.Registered }}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-app-muted">Pending</span>
						<span class="font-medium text-app-warning">{{ gosiSummary.data.counts.Pending }}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-app-muted">Not Registered</span>
						<span class="font-medium text-app-danger">{{ gosiSummary.data.counts['Not Registered'] }}</span>
					</div>
				</div>
			</SectionCard>
		</div>
	</template>
</template>
