<script setup lang="ts">
import SectionCard from './SectionCard.vue'

export interface ActionItem {
	label: string
	href: string
	icon: any
}

defineProps<{ actions: ActionItem[] }>()
</script>

<template>
	<SectionCard title="Quick Actions">
		<div class="space-y-1">
			<a
				v-for="action in actions"
				:key="action.label"
				:href="action.href"
				class="flex items-center gap-2 rounded-app-sm px-2 py-1.5 text-[13px] leading-[16px] text-app-primary hover:bg-app-bg"
			>
				<component :is="action.icon" :size="14" class="shrink-0" />
				<span>{{ action.label }}</span>
			</a>
		</div>
	</SectionCard>
</template>
