<script setup lang="ts">
import { Search } from 'lucide-vue-next'

withDefaults(defineProps<{ modelValue: string; placeholder?: string }>(), {
	placeholder: 'Search...',
})
defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
	<div class="relative">
		<Search :size="16" class="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-app-disabled" />
		<input
			type="text"
			:value="modelValue"
			:placeholder="placeholder"
			class="h-[36px] w-full rounded-app-sm border border-app-border bg-app-surface pl-8 pr-3 text-[14px] leading-[20px] text-app-text placeholder-app-disabled outline-none transition-colors focus:border-app-primary"
			@input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
		/>
	</div>
</template>
