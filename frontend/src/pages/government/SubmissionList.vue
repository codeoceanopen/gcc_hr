<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createListResource, call, toast, Button, Dialog, FormControl } from 'frappe-ui'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { governmentSubmissionTone } from '@/utils/format'

const router = useRouter()

const submissions = createListResource({
	doctype: 'Government Submission',
	fields: ['name', 'company', 'submission_type', 'status', 'outcome', 'generated_on', 'submitted_on'],
	orderBy: 'modified desc',
	pageLength: 100,
	auto: true,
})

const dialogOpen = ref(false)
const creating = ref(false)
const form = reactive({ company: '', submission_type: '' })

function openCreate() {
	form.company = ''
	form.submission_type = ''
	dialogOpen.value = true
}

async function create() {
	if (!form.company || !form.submission_type) {
		toast.error('Company and Submission Type are required.')
		return
	}
	creating.value = true
	try {
		const name = await call('gcc_hr.api.government.create_submission', { ...form })
		toast.success('Government Submission created.')
		dialogOpen.value = false
		router.push(`/government/${name}`)
	} catch {
		toast.error('Could not create submission.')
	} finally {
		creating.value = false
	}
}
</script>

<template>
	<div>
		<PageHeader
			title="Government Integration"
			description="Generate, validate, and track government submissions -- filed manually on the real portal, since no verified government API exists to call on your behalf."
		>
			<template #action>
				<Button variant="solid" @click="openCreate">New Submission</Button>
			</template>
		</PageHeader>

		<div class="p-6">
			<div v-if="submissions.loading && !submissions.data" class="text-sm text-gray-500">Loading...</div>

			<div v-else-if="!submissions.data?.length" class="text-sm text-gray-500">No Government Submissions yet.</div>

			<div v-else class="overflow-hidden rounded-xl border bg-white">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 text-left text-xs uppercase text-gray-500">
						<tr>
							<th class="px-4 py-2 font-medium">Name</th>
							<th class="px-4 py-2 font-medium">Company</th>
							<th class="px-4 py-2 font-medium">Type</th>
							<th class="px-4 py-2 font-medium">Status</th>
							<th class="px-4 py-2 font-medium">Outcome</th>
							<th class="px-4 py-2 font-medium">Submitted</th>
						</tr>
					</thead>
					<tbody class="divide-y">
						<tr
							v-for="s in submissions.data"
							:key="s.name"
							class="cursor-pointer hover:bg-gray-50"
							@click="router.push(`/government/${s.name}`)"
						>
							<td class="px-4 py-2.5 font-medium text-gray-900">{{ s.name }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ s.company }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ s.submission_type }}</td>
							<td class="px-4 py-2.5"><StatusBadge :label="s.status" :tone="governmentSubmissionTone(s.status)" /></td>
							<td class="px-4 py-2.5 text-gray-600">{{ s.outcome || '—' }}</td>
							<td class="px-4 py-2.5 text-gray-600">{{ s.submitted_on || '—' }}</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<Dialog v-model="dialogOpen" :options="{ title: 'New Government Submission' }">
			<template #body-content>
				<div class="space-y-4">
					<FormControl v-model="form.company" label="Company" type="text" required description="e.g. glob" />
					<FormControl
						v-model="form.submission_type"
						label="Submission Type"
						type="text"
						required
						description="e.g. SA_NITAQAT_REPORT"
					/>
				</div>
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="creating" @click="create">Create</Button>
					<Button variant="outline" @click="dialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>
