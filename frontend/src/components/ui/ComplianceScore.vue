<script setup lang="ts">
import StatusBadge from './StatusBadge.vue'
import { complianceTone } from '@/utils/format'

defineProps<{ score: number; status: string }>()

function barColor(score: number) {
	if (score >= 75) return 'bg-app-success'
	if (score >= 50) return 'bg-app-warning'
	return 'bg-app-danger'
}
</script>

<template>
	<div>
		<div class="flex items-center justify-between">
			<p class="text-[13px] leading-[16px] text-app-muted">Compliance Score</p>
			<StatusBadge :label="status" :tone="complianceTone(status)" />
		</div>
		<div class="mt-2 flex items-center gap-3">
			<p class="text-[24px] font-semibold leading-[28px] text-app-text">{{ score }}%</p>
			<div class="h-1.5 flex-1 overflow-hidden rounded-full bg-gray-100">
				<div class="h-full rounded-full transition-all" :class="barColor(score)" :style="{ width: `${Math.min(100, Math.max(0, score))}%` }" />
			</div>
		</div>
	</div>
</template>
