<script setup lang="ts">
withDefaults(defineProps<{ rows?: number }>(), { rows: 4 })
</script>

<template>
	<div class="space-y-2 p-4">
		<div v-for="i in rows" :key="i" class="h-4 animate-pulse rounded bg-gray-100" :style="{ width: i % 2 === 0 ? '85%' : '100%' }" />
	</div>
</template>
