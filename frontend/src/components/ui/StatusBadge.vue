<script setup lang="ts">
defineProps({
	label: { type: String, required: true },
	tone: { type: String, default: 'neutral' }, // success | warning | danger | info | neutral
})

// Frappe-style restrained status color: a small dot + light surface + dark
// readable text, never a solid-colored block (see DESIGN.md's status color
// rules). `app-*` tokens from tailwind.config.js, not raw Tailwind palette
// colors, so this stays in sync if the palette ever changes in one place.
const toneClasses: Record<string, string> = {
	success: 'bg-app-success-surface text-[#1c7430]',
	warning: 'bg-app-warning-surface text-[#92600a]',
	danger: 'bg-app-danger-surface text-[#9c2126]',
	info: 'bg-app-info-surface text-[#155ea8]',
	neutral: 'bg-gray-100 text-app-muted',
}

const dotClasses: Record<string, string> = {
	success: 'bg-app-success',
	warning: 'bg-app-warning',
	danger: 'bg-app-danger',
	info: 'bg-app-info',
	neutral: 'bg-app-disabled',
}
</script>

<template>
	<span
		class="inline-flex items-center gap-1.5 rounded-app-sm px-2 py-0.5 text-xs font-medium leading-4"
		:class="toneClasses[tone] || toneClasses.neutral"
	>
		<span class="h-1.5 w-1.5 shrink-0 rounded-full" :class="dotClasses[tone] || dotClasses.neutral" />
		{{ label }}
	</span>
</template>
