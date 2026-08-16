<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'

interface Crumb {
	label: string
	route?: string
}

defineProps<{ items: Crumb[] }>()
</script>

<template>
	<nav class="flex items-center gap-1.5 px-4 pt-3 text-[13px] leading-[16px] text-app-muted sm:px-6">
		<template v-for="(item, index) in items" :key="item.label">
			<router-link v-if="item.route" :to="item.route" class="hover:text-app-text">
				{{ item.label }}
			</router-link>
			<span v-else :class="index === items.length - 1 ? 'text-app-text' : ''">{{ item.label }}</span>
			<ChevronRight v-if="index < items.length - 1" :size="14" class="shrink-0 text-app-disabled" />
		</template>
	</nav>
</template>
