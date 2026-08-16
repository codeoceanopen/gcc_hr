<script setup lang="ts">
import { Button } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
	<div class="flex h-full flex-col items-center justify-center gap-3 text-center">
		<p class="text-lg font-medium text-gray-700">Page not found</p>
		<Button variant="outline" @click="router.push('/')">Back to Command Center</Button>
	</div>
</template>
