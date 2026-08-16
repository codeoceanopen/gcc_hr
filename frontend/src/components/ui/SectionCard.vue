<script setup lang="ts">
defineProps({
	title: { type: String, default: '' },
	description: { type: String, default: '' },
	// No padding on the body -- useful when the slot content is a table
	// that needs to run edge-to-edge inside the card.
	noPadding: { type: Boolean, default: false },
})
</script>

<template>
	<div class="rounded-app-md border border-app-border bg-app-surface">
		<div v-if="title || $slots.action" class="flex items-center justify-between gap-4 border-b border-app-border px-4 py-3">
			<div>
				<h2 v-if="title" class="text-[16px] font-semibold leading-[20px] text-app-text">{{ title }}</h2>
				<p v-if="description" class="mt-0.5 text-[13px] leading-[16px] text-app-muted">{{ description }}</p>
			</div>
			<div class="flex shrink-0 items-center gap-2">
				<slot name="action" />
			</div>
		</div>
		<div :class="noPadding ? '' : 'p-4'">
			<slot />
		</div>
	</div>
</template>
