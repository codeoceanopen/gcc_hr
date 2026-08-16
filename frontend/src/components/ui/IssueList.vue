<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import SectionCard from './SectionCard.vue'
import { relativeDays } from '@/utils/format'

export interface IssueRow {
	label: string
	reference: string
	date: string
	severity: 'danger' | 'warning'
}

defineProps<{ issues: IssueRow[] }>()
</script>

<template>
	<SectionCard title="Recent Critical Issues">
		<div v-if="!issues.length" class="py-6 text-center text-[13px] text-app-muted">Nothing urgent right now.</div>
		<div v-else class="space-y-3">
			<div v-for="(issue, index) in issues" :key="index" class="flex items-start gap-2 text-[13px]">
				<AlertTriangle :size="14" class="mt-0.5 shrink-0" :class="issue.severity === 'danger' ? 'text-app-danger' : 'text-app-warning'" />
				<div class="min-w-0 flex-1">
					<p class="font-medium leading-[16px] text-app-text">{{ issue.label }}</p>
					<p class="mt-0.5 leading-[16px] text-app-muted">{{ issue.reference }}</p>
				</div>
				<span class="shrink-0 text-[12px] leading-[16px] text-app-disabled">{{ relativeDays(issue.date) }}</span>
			</div>
		</div>
	</SectionCard>
</template>
