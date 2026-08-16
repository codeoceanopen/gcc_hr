<script setup lang="ts">
import { FrappeUIProvider, Dialogs } from 'frappe-ui'
</script>

<template>
	<FrappeUIProvider>
		<router-view />
		<Dialogs />
	</FrappeUIProvider>
</template>
