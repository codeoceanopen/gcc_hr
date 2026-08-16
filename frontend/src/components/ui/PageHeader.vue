<script setup lang="ts">
defineProps({
	title: { type: String, required: true },
	description: { type: String, default: '' },
})
</script>

<template>
	<div class="border-b border-app-border bg-app-surface px-4 py-4 sm:px-6">
		<div class="flex items-center justify-between gap-4">
			<div>
				<h1 class="text-[24px] font-semibold leading-[28px] text-app-text">{{ title }}</h1>
				<p v-if="description" class="mt-1 text-[14px] leading-[20px] text-app-muted">{{ description }}</p>
			</div>
			<div class="flex shrink-0 items-center gap-2">
				<slot name="action" />
			</div>
		</div>
	</div>
</template>
