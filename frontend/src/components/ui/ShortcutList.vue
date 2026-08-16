<script setup lang="ts">
import SectionCard from './SectionCard.vue'

export interface ShortcutItem {
	label: string
	route: string
	icon: any
}

defineProps<{ shortcuts: ShortcutItem[]; emptyText?: string }>()
</script>

<template>
	<SectionCard title="Shortcuts">
		<div v-if="!shortcuts.length" class="py-4 text-center text-[13px] text-app-muted">
			{{ emptyText || 'No shortcuts for this company yet.' }}
		</div>
		<div v-else class="space-y-1">
			<router-link
				v-for="shortcut in shortcuts"
				:key="shortcut.label"
				:to="shortcut.route"
				class="flex items-center gap-2 rounded-app-sm px-2 py-1.5 text-[13px] leading-[16px] text-app-primary hover:bg-app-bg"
			>
				<component :is="shortcut.icon" :size="14" class="shrink-0" />
				<span>{{ shortcut.label }}</span>
			</router-link>
		</div>
	</SectionCard>
</template>
