<script setup lang="ts">
import { computed, reactive } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { ShieldCheck, CalendarRange, Check } from 'lucide-vue-next'
import SectionCard from './SectionCard.vue'

const props = defineProps<{
	status: string
	trendMonths: number
}>()

const emit = defineEmits<{
	apply: [{ status: string; trendMonths: number }]
}>()

// Local draft state -- filters only take effect on [Apply Filters], matching
// the reference design's explicit apply step rather than filtering on every
// keystroke/selection.
const draft = reactive({ status: props.status, trendMonths: props.trendMonths })

const isDirty = computed(() => draft.status !== props.status || draft.trendMonths !== props.trendMonths)

function apply() {
	emit('apply', { status: draft.status, trendMonths: draft.trendMonths })
}
</script>

<template>
	<SectionCard title="Quick Filters">
		<div class="space-y-3">
			<div class="grid grid-cols-2 gap-3">
				<div>
					<label class="mb-1.5 flex items-center gap-1.5 text-[12px] font-medium leading-[16px] text-app-muted">
						<ShieldCheck :size="13" class="shrink-0 text-app-disabled" />
						Compliance Status
					</label>
					<FormControl
						v-model="draft.status"
						type="select"
						variant="outline"
						class="w-full"
						:options="[
							{ label: 'All Statuses', value: '' },
							{ label: 'Compliant', value: 'Compliant' },
							{ label: 'Warning', value: 'Warning' },
							{ label: 'Critical', value: 'Critical' },
							{ label: 'Blocked', value: 'Blocked' },
						]"
					/>
				</div>

				<div>
					<label class="mb-1.5 flex items-center gap-1.5 text-[12px] font-medium leading-[16px] text-app-muted">
						<CalendarRange :size="13" class="shrink-0 text-app-disabled" />
						Trend Range
					</label>
					<FormControl
						v-model.number="draft.trendMonths"
						type="select"
						variant="outline"
						class="w-full"
						:options="[
							{ label: 'Last 3 Months', value: 3 },
							{ label: 'Last 6 Months', value: 6 },
							{ label: 'Last 12 Months', value: 12 },
						]"
					/>
				</div>
			</div>

			<Button variant="solid" theme="blue" class="w-full justify-center" @click="apply">
				<template #prefix>
					<Check :size="14" />
				</template>
				Apply Filters
				<template #suffix>
					<span v-if="isDirty" class="h-1.5 w-1.5 rounded-full bg-white/70" />
				</template>
			</Button>
		</div>
	</SectionCard>
</template>
