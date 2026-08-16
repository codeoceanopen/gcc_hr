<script setup lang="ts">
import { reactive, watch } from 'vue'
import { createDocumentResource, toast, Button, FormControl } from 'frappe-ui'

const props = defineProps<{ employee: string }>()

const kuwaitProfile = createDocumentResource({
	doctype: 'Kuwait Employee Profile',
	name: props.employee,
	auto: true,
})

const NATIONALITY_OPTIONS = ['Kuwaiti', 'Non-Kuwaiti']

const form = reactive({
	nationality_status: 'Non-Kuwaiti',
	civil_id_number: '',
	civil_id_expiry: '',
	work_permit_number: '',
	work_permit_expiry: '',
	sponsor: '',
	profession: '',
	wps_registered: 0,
})

watch(
	() => kuwaitProfile.doc,
	(doc: any) => {
		if (!doc) return
		form.nationality_status = doc.nationality_status
		form.civil_id_number = doc.civil_id_number || ''
		form.civil_id_expiry = doc.civil_id_expiry || ''
		form.work_permit_number = doc.work_permit_number || ''
		form.work_permit_expiry = doc.work_permit_expiry || ''
		form.sponsor = doc.sponsor || ''
		form.profession = doc.profession || ''
		form.wps_registered = doc.wps_registered || 0
	},
	{ immediate: true },
)

async function save() {
	try {
		await kuwaitProfile.setValue.submit({ ...form })
		toast.success('Kuwait employee details updated.')
	} catch {
		toast.error('Could not update Kuwait employee details.')
	}
}
</script>

<template>
	<div v-if="kuwaitProfile.doc" class="rounded-xl border bg-white p-4">
		<p class="mb-3 text-sm font-medium text-gray-700">Kuwait -- Identity &amp; Permits</p>
		<div class="grid grid-cols-2 gap-3">
			<FormControl v-model="form.nationality_status" label="Kuwaiti / Non-Kuwaiti" type="select" :options="NATIONALITY_OPTIONS" />
			<FormControl v-model="form.wps_registered" label="WPS Registered" type="checkbox" />
			<FormControl v-model="form.civil_id_number" label="Civil ID Number" type="text" />
			<FormControl v-model="form.civil_id_expiry" label="Civil ID Expiry" type="date" />
			<FormControl v-model="form.work_permit_number" label="Work Permit Number" type="text" />
			<FormControl v-model="form.work_permit_expiry" label="Work Permit Expiry" type="date" />
			<FormControl v-model="form.sponsor" label="Sponsor / Employer" type="text" />
			<FormControl v-model="form.profession" label="Profession" type="text" />
		</div>
		<div class="mt-4 flex justify-end">
			<Button variant="solid" :loading="kuwaitProfile.setValue.loading" @click="save">Save</Button>
		</div>
	</div>
</template>
