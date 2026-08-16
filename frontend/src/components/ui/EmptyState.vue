<script setup lang="ts">
withDefaults(defineProps<{ title: string; description?: string }>(), { description: '' })
</script>

<template>
	<div class="flex flex-col items-center justify-center gap-1 px-4 py-12 text-center">
		<p class="text-[14px] font-medium leading-[20px] text-app-text">{{ title }}</p>
		<p v-if="description" class="text-[13px] leading-[16px] text-app-muted">{{ description }}</p>
		<div v-if="$slots.action" class="mt-3">
			<slot name="action" />
		</div>
	</div>
</template>
