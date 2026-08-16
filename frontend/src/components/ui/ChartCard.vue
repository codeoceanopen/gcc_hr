<script setup lang="ts">
import { computed } from 'vue'
import { AxisChart, DonutChart } from 'frappe-ui'
import SectionCard from './SectionCard.vue'

const props = defineProps<{
	title: string
	description?: string
	type: 'axis' | 'donut'
	config: Record<string, any>
}>()

// SectionCard already renders `title` as the card header -- always clear the
// chart's own internal title so it never duplicates it inside the canvas.
const chartConfig = computed(() => ({ ...props.config, title: '' }))
</script>

<template>
	<SectionCard :title="title" :description="description">
		<AxisChart v-if="type === 'axis'" :config="chartConfig" />
		<DonutChart v-else :config="chartConfig" />
		<slot />
	</SectionCard>
</template>
