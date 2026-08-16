<script setup lang="ts">
withDefaults(defineProps<{ title?: string; description?: string }>(), {
	title: 'Something went wrong',
	description: 'Please try again.',
})
const emit = defineEmits<{ retry: [] }>()
</script>

<template>
	<div class="flex flex-col items-center justify-center gap-1 px-4 py-12 text-center">
		<p class="text-[14px] font-medium leading-[20px] text-app-text">{{ title }}</p>
		<p class="text-[13px] leading-[16px] text-app-muted">{{ description }}</p>
		<button
			type="button"
			class="mt-3 h-[36px] rounded-app-sm border border-app-border bg-app-surface px-3 text-[13px] font-medium text-app-text hover:bg-gray-50"
			@click="emit('retry')"
		>
			Try Again
		</button>
	</div>
</template>
