<script setup lang="ts">
import SectionCard from './SectionCard.vue'

export interface ExpiryRow {
	document_type: string
	count: number
}

defineProps<{
	title?: string
	rows: ExpiryRow[]
	emptyText?: string
}>()
</script>

<template>
	<SectionCard :title="title || 'Documents Expiry (Next 30 Days)'">
		<div v-if="!rows.length" class="py-6 text-center text-[13px] text-app-muted">
			{{ emptyText || 'Nothing expiring soon.' }}
		</div>
		<div v-else class="space-y-2">
			<div v-for="row in rows" :key="row.document_type" class="flex items-center justify-between text-[13px]">
				<span class="text-app-text">{{ row.document_type }}</span>
				<span class="font-medium text-app-warning">{{ row.count }}</span>
			</div>
		</div>
	</SectionCard>
</template>
