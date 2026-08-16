<script setup lang="ts">
interface Tab {
	key: string
	label: string
}

const props = defineProps<{ tabs: Tab[]; modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

function select(key: string) {
	emit('update:modelValue', key)
}
</script>

<template>
	<div class="border-b border-app-border">
		<nav class="-mb-px flex gap-5 px-4 sm:px-6">
			<button
				v-for="tab in tabs"
				:key="tab.key"
				type="button"
				class="border-b-2 py-2.5 text-[13px] font-medium leading-[16px] transition-colors"
				:class="
					tab.key === props.modelValue
						? 'border-app-primary text-app-primary'
						: 'border-transparent text-app-muted hover:text-app-text'
				"
				@click="select(tab.key)"
			>
				{{ tab.label }}
			</button>
		</nav>
	</div>
</template>
