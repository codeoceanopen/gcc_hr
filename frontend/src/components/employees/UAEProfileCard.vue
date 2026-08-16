<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createDocumentResource, toast, Button, FormControl } from 'frappe-ui'

const props = defineProps<{ employee: string }>()

const uaeProfile = createDocumentResource({
	doctype: 'UAE Employee Profile',
	name: props.employee,
	auto: true,
})

const NATIONALITY_OPTIONS = ['Emirati', 'Non-Emirati']

const form = reactive({
	nationality_status: 'Non-Emirati',
	eid_number: '',
	eid_expiry: '',
	work_permit_number: '',
	work_permit_expiry: '',
	sponsor: '',
	profession: '',
	wps_registered: 0,
	wps_bank_name: '',
})

watch(
	() => uaeProfile.doc,
	(doc: any) => {
		if (!doc) return
		form.nationality_status = doc.nationality_status
		form.eid_number = doc.eid_number || ''
		form.eid_expiry = doc.eid_expiry || ''
		form.work_permit_number = doc.work_permit_number || ''
		form.work_permit_expiry = doc.work_permit_expiry || ''
		form.sponsor = doc.sponsor || ''
		form.profession = doc.profession || ''
		form.wps_registered = doc.wps_registered || 0
		form.wps_bank_name = doc.wps_bank_name || ''
	},
	{ immediate: true },
)

async function save() {
	try {
		await uaeProfile.setValue.submit({ ...form })
		toast.success('UAE employee details updated.')
	} catch {
		toast.error('Could not update UAE employee details.')
	}
}
</script>

<template>
	<div v-if="uaeProfile.doc" class="rounded-xl border bg-white p-4">
		<p class="mb-3 text-sm font-medium text-gray-700">UAE -- Identity &amp; Permits</p>
		<div class="grid grid-cols-2 gap-3">
			<FormControl v-model="form.nationality_status" label="Emirati / Non-Emirati" type="select" :options="NATIONALITY_OPTIONS" />
			<FormControl v-model="form.wps_registered" label="WPS Registered" type="checkbox" />
			<FormControl v-model="form.eid_number" label="EID Number" type="text" />
			<FormControl v-model="form.eid_expiry" label="EID Expiry" type="date" />
			<FormControl v-model="form.work_permit_number" label="Work Permit Number" type="text" />
			<FormControl v-model="form.work_permit_expiry" label="Work Permit Expiry" type="date" />
			<FormControl v-model="form.sponsor" label="Sponsor / Employer" type="text" />
			<FormControl v-model="form.profession" label="Profession" type="text" />
			<FormControl v-model="form.wps_bank_name" label="WPS Bank Name" type="text" />
		</div>
		<div class="mt-4 flex justify-end">
			<Button variant="solid" :loading="uaeProfile.setValue.loading" @click="save">Save</Button>
		</div>
	</div>
</template>
