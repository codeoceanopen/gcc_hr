<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createDocumentResource, toast, Button, FormControl } from 'frappe-ui'

const props = defineProps<{ employee: string }>()

const omanProfile = createDocumentResource({
	doctype: 'Oman Employee Profile',
	name: props.employee,
	auto: true,
})

const NATIONALITY_OPTIONS = ['Omani', 'Non-Omani']

const form = reactive({
	nationality_status: 'Non-Omani',
	resident_card_number: '',
	resident_card_expiry: '',
	work_permit_number: '',
	work_permit_expiry: '',
	sponsor: '',
	profession: '',
	pasi_registered: 0,
	wps_registered: 0,
})

watch(
	() => omanProfile.doc,
	(doc: any) => {
		if (!doc) return
		form.nationality_status = doc.nationality_status
		form.resident_card_number = doc.resident_card_number || ''
		form.resident_card_expiry = doc.resident_card_expiry || ''
		form.work_permit_number = doc.work_permit_number || ''
		form.work_permit_expiry = doc.work_permit_expiry || ''
		form.sponsor = doc.sponsor || ''
		form.profession = doc.profession || ''
		form.pasi_registered = doc.pasi_registered || 0
		form.wps_registered = doc.wps_registered || 0
	},
	{ immediate: true },
)

async function save() {
	try {
		await omanProfile.setValue.submit({ ...form })
		toast.success('Oman employee details updated.')
	} catch {
		toast.error('Could not update Oman employee details.')
	}
}
</script>

<template>
	<div v-if="omanProfile.doc" class="rounded-xl border bg-white p-4">
		<p class="mb-3 text-sm font-medium text-gray-700">Oman -- Identity &amp; Permits</p>
		<div class="grid grid-cols-2 gap-3">
			<FormControl v-model="form.nationality_status" label="Omani / Non-Omani" type="select" :options="NATIONALITY_OPTIONS" />
			<FormControl v-model="form.pasi_registered" label="PASI Registered" type="checkbox" />
			<FormControl v-model="form.resident_card_number" label="Resident Card Number" type="text" />
			<FormControl v-model="form.resident_card_expiry" label="Resident Card Expiry" type="date" />
			<FormControl v-model="form.work_permit_number" label="Work Permit Number" type="text" />
			<FormControl v-model="form.work_permit_expiry" label="Work Permit Expiry" type="date" />
			<FormControl v-model="form.sponsor" label="Sponsor / Employer" type="text" />
			<FormControl v-model="form.profession" label="Profession" type="text" />
			<FormControl v-model="form.wps_registered" label="WPS Registered" type="checkbox" />
		</div>
		<div class="mt-4 flex justify-end">
			<Button variant="solid" :loading="omanProfile.setValue.loading" @click="save">Save</Button>
		</div>
	</div>
</template>
