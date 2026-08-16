<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createDocumentResource, toast, Button, FormControl } from 'frappe-ui'

const props = defineProps<{ employee: string }>()

const bahrainProfile = createDocumentResource({
	doctype: 'Bahrain Employee Profile',
	name: props.employee,
	auto: true,
})

const NATIONALITY_OPTIONS = ['Bahraini', 'Non-Bahraini']

const form = reactive({
	nationality_status: 'Non-Bahraini',
	cpr_number: '',
	cpr_expiry: '',
	work_permit_number: '',
	work_permit_expiry: '',
	sponsor: '',
	profession: '',
	sio_registered: 0,
	wps_registered: 0,
})

watch(
	() => bahrainProfile.doc,
	(doc: any) => {
		if (!doc) return
		form.nationality_status = doc.nationality_status
		form.cpr_number = doc.cpr_number || ''
		form.cpr_expiry = doc.cpr_expiry || ''
		form.work_permit_number = doc.work_permit_number || ''
		form.work_permit_expiry = doc.work_permit_expiry || ''
		form.sponsor = doc.sponsor || ''
		form.profession = doc.profession || ''
		form.sio_registered = doc.sio_registered || 0
		form.wps_registered = doc.wps_registered || 0
	},
	{ immediate: true },
)

async function save() {
	try {
		await bahrainProfile.setValue.submit({ ...form })
		toast.success('Bahrain employee details updated.')
	} catch {
		toast.error('Could not update Bahrain employee details.')
	}
}
</script>

<template>
	<div v-if="bahrainProfile.doc" class="rounded-xl border bg-white p-4">
		<p class="mb-3 text-sm font-medium text-gray-700">Bahrain -- Identity &amp; Permits</p>
		<div class="grid grid-cols-2 gap-3">
			<FormControl v-model="form.nationality_status" label="Bahraini / Non-Bahraini" type="select" :options="NATIONALITY_OPTIONS" />
			<FormControl v-model="form.sio_registered" label="SIO Registered" type="checkbox" />
			<FormControl v-model="form.cpr_number" label="CPR Number" type="text" />
			<FormControl v-model="form.cpr_expiry" label="CPR Expiry" type="date" />
			<FormControl v-model="form.work_permit_number" label="Work Permit Number" type="text" />
			<FormControl v-model="form.work_permit_expiry" label="Work Permit Expiry" type="date" />
			<FormControl v-model="form.sponsor" label="Sponsor / Employer" type="text" />
			<FormControl v-model="form.profession" label="Profession" type="text" />
			<FormControl v-model="form.wps_registered" label="WPS Registered" type="checkbox" />
		</div>
		<div class="mt-4 flex justify-end">
			<Button variant="solid" :loading="bahrainProfile.setValue.loading" @click="save">Save</Button>
		</div>
	</div>
</template>
