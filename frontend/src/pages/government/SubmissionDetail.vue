<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { createDocumentResource, call, toast, Button, Dialog, FormControl, FileUploader } from 'frappe-ui'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { governmentSubmissionTone } from '@/utils/format'

const props = defineProps<{ name: string }>()

const submission = createDocumentResource({
	doctype: 'Government Submission',
	name: props.name,
	auto: true,
})

const submissionType = ref<any>(null)
let loadedSubmissionTypeFor = ''

const acting = ref(false)

async function loadSubmissionType() {
	const typeName = submission.doc?.submission_type
	if (typeName && loadedSubmissionTypeFor !== typeName) {
		loadedSubmissionTypeFor = typeName
		submissionType.value = await call('frappe.client.get', { doctype: 'Government Submission Type', name: typeName })
	}
}

async function run(method: string, args: Record<string, unknown> = {}, successMessage = 'Done.') {
	acting.value = true
	try {
		await call(`gcc_hr.api.government.${method}`, { name: props.name, ...args })
		toast.success(successMessage)
		await submission.reload()
		await loadSubmissionType()
	} catch (err: any) {
		toast.error(err?.messages?.[0] || 'Action failed.')
	} finally {
		acting.value = false
	}
}

const submitDialogOpen = ref(false)
const submitForm = reactive({ government_reference_number: '' })
async function recordSubmission() {
	await run('record_manual_submission', { government_reference_number: submitForm.government_reference_number })
	submitDialogOpen.value = false
}

async function onResponseUploaded(fileDoc: { file_url: string }) {
	await run('upload_response', { file_url: fileDoc.file_url }, 'Response recorded.')
}

const completeDialogOpen = ref(false)
const completeForm = reactive({ outcome: 'Accepted', notes: '' })
async function completeSubmission() {
	await run('complete_submission', { outcome: completeForm.outcome, notes: completeForm.notes }, 'Submission completed.')
	completeDialogOpen.value = false
}

function downloadGeneratedDocument() {
	if (submission.doc?.generated_document) window.open(submission.doc.generated_document, '_blank')
}

function viewResponseDocument() {
	if (submission.doc?.response_document) window.open(submission.doc.response_document, '_blank')
}

watch(() => submission.doc?.submission_type, loadSubmissionType, { immediate: true })
</script>

<template>
	<div v-if="submission.doc">
		<PageHeader :title="submission.doc.name" :description="`${submission.doc.company} · ${submission.doc.submission_type}`" />

		<div class="space-y-6 p-6">
			<div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Status</p>
					<StatusBadge :label="submission.doc.status" :tone="governmentSubmissionTone(submission.doc.status)" />
				</div>
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Outcome</p>
					<p class="mt-1 text-sm font-medium text-gray-900">{{ submission.doc.outcome || '—' }}</p>
				</div>
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Generated On</p>
					<p class="mt-1 text-sm font-medium text-gray-900">{{ submission.doc.generated_on || '—' }}</p>
				</div>
				<div class="rounded-xl border bg-white p-4">
					<p class="text-xs uppercase tracking-wide text-gray-400">Submitted On</p>
					<p class="mt-1 text-sm font-medium text-gray-900">{{ submission.doc.submitted_on || '—' }}</p>
				</div>
			</div>

			<div v-if="submissionType" class="rounded-xl border bg-amber-50 p-4 text-sm text-amber-900">
				<p class="font-medium">No verified government API is called for this submission.</p>
				<p class="mt-1">
					File it manually at
					<a :href="submissionType.portal_url" target="_blank" class="underline">{{ submissionType.portal_url }}</a>
					, then come back and record what happened below.
				</p>
				<p v-if="submissionType.portal_instructions" class="mt-1 text-amber-800">
					{{ submissionType.portal_instructions }}
				</p>
			</div>

			<div class="rounded-xl border bg-white p-4">
				<p class="mb-3 text-sm font-medium text-gray-700">Actions</p>

				<div v-if="submission.doc.validation_errors" class="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">
					<p class="font-medium">Validation errors:</p>
					<pre class="whitespace-pre-wrap">{{ submission.doc.validation_errors }}</pre>
				</div>

				<div class="flex flex-wrap gap-2">
					<Button v-if="['Draft', 'Generated', 'Validated', 'Ready for Submission'].includes(submission.doc.status)"
						variant="outline" :loading="acting" @click="run('generate', {}, 'Document generated.')">
						{{ submission.doc.status === 'Draft' ? 'Generate' : 'Regenerate' }}
					</Button>

					<Button v-if="submission.doc.generated_document" variant="outline" @click="downloadGeneratedDocument">
						Download Generated Document
					</Button>

					<Button v-if="submission.doc.status === 'Generated'" variant="solid" :loading="acting"
						@click="run('validate_submission', {}, 'Validated.')">
						Validate
					</Button>

					<Button v-if="submission.doc.status === 'Validated'" variant="solid" :loading="acting"
						@click="run('mark_ready', {}, 'Marked ready for submission.')">
						Mark Ready for Submission
					</Button>

					<Button v-if="submission.doc.status === 'Ready for Submission'" variant="solid"
						@click="submitDialogOpen = true">
						Record Manual Submission
					</Button>

					<FileUploader v-if="submission.doc.status === 'Submitted'"
						:upload-args="{ doctype: 'Government Submission', docname: submission.doc.name, private: true }"
						@success="onResponseUploaded">
						<template #default="{ progress, uploading, openFileSelector }">
							<Button variant="solid" :loading="uploading" @click="openFileSelector">
								{{ uploading ? `Uploading ${progress}%` : 'Upload Response Document' }}
							</Button>
						</template>
					</FileUploader>

					<Button v-if="submission.doc.response_document" variant="outline" @click="viewResponseDocument">
						View Response Document
					</Button>

					<Button v-if="submission.doc.status === 'Response Uploaded'" variant="solid" @click="completeDialogOpen = true">
						Complete
					</Button>
				</div>
			</div>

			<div v-if="submission.doc.notes" class="rounded-xl border bg-white p-4">
				<p class="mb-1 text-sm font-medium text-gray-700">Notes</p>
				<p class="text-sm text-gray-600">{{ submission.doc.notes }}</p>
			</div>
		</div>

		<Dialog v-model="submitDialogOpen" :options="{ title: 'Record Manual Submission' }">
			<template #body-content>
				<p class="mb-3 text-sm text-gray-500">
					Confirms you have manually filed this on the real government portal.
				</p>
				<FormControl v-model="submitForm.government_reference_number" label="Government Reference Number" type="text" />
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="acting" @click="recordSubmission">Record</Button>
					<Button variant="outline" @click="submitDialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>

		<Dialog v-model="completeDialogOpen" :options="{ title: 'Complete Submission' }">
			<template #body-content>
				<div class="space-y-4">
					<FormControl
						v-model="completeForm.outcome"
						label="Outcome"
						type="select"
						:options="['Accepted', 'Rejected']"
					/>
					<FormControl v-model="completeForm.notes" label="Notes" type="textarea" />
				</div>
			</template>
			<template #actions>
				<div class="flex flex-row-reverse gap-2">
					<Button variant="solid" :loading="acting" @click="completeSubmission">Complete</Button>
					<Button variant="outline" @click="completeDialogOpen = false">Cancel</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>
