<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import AppHeader from './AppHeader.vue'
</script>

<template>
	<div class="flex h-screen overflow-hidden bg-app-bg">
		<Sidebar />
		<div class="flex min-w-0 flex-1 flex-col">
			<AppHeader />
			<main class="flex-1 overflow-y-auto">
				<router-view />
			</main>
		</div>
	</div>
</template>
