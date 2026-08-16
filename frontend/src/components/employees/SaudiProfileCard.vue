<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createDocumentResource, toast, Button, FormControl } from 'frappe-ui'

const props = defineProps<{ employee: string }>()

const saudiProfile = createDocumentResource({
	doctype: 'Saudi Employee Profile',
	name: props.employee,
	auto: true,
})

const NATIONALITY_OPTIONS = ['Saudi', 'Non-Saudi']
const QIWA_OPTIONS = ['Not Registered', 'Pending', 'Approved', 'Rejected']

const form = reactive({
	nationality_status: 'Non-Saudi',
	iqama_number: '',
	iqama_expiry: '',
	work_permit_number: '',
	work_permit_expiry: '',
	sponsor: '',
	profession: '',
	qiwa_contract_status: 'Not Registered',
})

watch(
	() => saudiProfile.doc,
	(doc: any) => {
		if (!doc) return
		form.nationality_status = doc.nationality_status
		form.iqama_number = doc.iqama_number || ''
		form.iqama_expiry = doc.iqama_expiry || ''
		form.work_permit_number = doc.work_permit_number || ''
		form.work_permit_expiry = doc.work_permit_expiry || ''
		form.sponsor = doc.sponsor || ''
		form.profession = doc.profession || ''
		form.qiwa_contract_status = doc.qiwa_contract_status || 'Not Registered'
	},
	{ immediate: true },
)

async function save() {
	try {
		await saudiProfile.setValue.submit({ ...form })
		toast.success('Saudi employee details updated.')
	} catch {
		toast.error('Could not update Saudi employee details.')
	}
}
</script>

<template>
	<div v-if="saudiProfile.doc" class="rounded-xl border bg-white p-4">
		<p class="mb-3 text-sm font-medium text-gray-700">Saudi Arabia -- Identity &amp; Permits</p>
		<div class="grid grid-cols-2 gap-3">
			<FormControl v-model="form.nationality_status" label="Saudi / Non-Saudi" type="select" :options="NATIONALITY_OPTIONS" />
			<FormControl v-model="form.qiwa_contract_status" label="Qiwa Contract Status" type="select" :options="QIWA_OPTIONS" />
			<FormControl v-model="form.iqama_number" label="Iqama Number" type="text" />
			<FormControl v-model="form.iqama_expiry" label="Iqama Expiry" type="date" />
			<FormControl v-model="form.work_permit_number" label="Work Permit Number" type="text" />
			<FormControl v-model="form.work_permit_expiry" label="Work Permit Expiry" type="date" />
			<FormControl v-model="form.sponsor" label="Sponsor" type="text" />
			<FormControl v-model="form.profession" label="Profession" type="text" />
		</div>
		<div class="mt-4 flex justify-end">
			<Button variant="solid" :loading="saudiProfile.setValue.loading" @click="save">Save</Button>
		</div>
	</div>
</template>
