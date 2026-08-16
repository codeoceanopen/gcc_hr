<script setup lang="ts">
withDefaults(
	defineProps<{
		label: string
		value: string | number
		hint?: string
		tone?: 'neutral' | 'success' | 'warning' | 'danger'
	}>(),
	{ hint: '', tone: 'neutral' },
)

const hintClasses: Record<string, string> = {
	neutral: 'text-app-muted',
	success: 'text-app-success',
	warning: 'text-app-warning',
	danger: 'text-app-danger',
}
</script>

<template>
	<div class="rounded-app-md border border-app-border bg-app-surface p-4">
		<p class="text-[13px] leading-[16px] text-app-muted">{{ label }}</p>
		<p class="mt-1.5 text-[24px] font-semibold leading-[28px] text-app-text">{{ value }}</p>
		<p v-if="hint" class="mt-1 text-[12px] leading-[16px]" :class="hintClasses[tone]">{{ hint }}</p>
	</div>
</template>
