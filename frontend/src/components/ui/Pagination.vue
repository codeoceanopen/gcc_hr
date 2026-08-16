<script setup lang="ts">
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

// Accepts a frappe-ui createListResource instance directly (start/
// pageLength/hasNextPage/next()/previous() are all already on it -- see
// frappe-ui/src/resources/listResource.js) rather than re-deriving that
// state in every page that lists something.
const props = defineProps<{ resource: any }>()

const rangeStart = () => (props.resource.data?.length ? props.resource.start + 1 : 0)
const rangeEnd = () => props.resource.start + (props.resource.data?.length || 0)
</script>

<template>
	<div class="flex items-center justify-between border-t border-app-border px-4 py-2.5">
		<p class="text-[13px] leading-[16px] text-app-muted">
			Showing {{ rangeStart() }}-{{ rangeEnd() }}
		</p>
		<div class="flex items-center gap-1">
			<button
				type="button"
				class="flex h-[28px] w-[28px] items-center justify-center rounded-app-sm border border-app-border text-app-text disabled:cursor-not-allowed disabled:text-app-disabled"
				:disabled="resource.start === 0"
				@click="resource.previous()"
			>
				<ChevronLeft :size="16" />
			</button>
			<button
				type="button"
				class="flex h-[28px] w-[28px] items-center justify-center rounded-app-sm border border-app-border text-app-text disabled:cursor-not-allowed disabled:text-app-disabled"
				:disabled="!resource.hasNextPage"
				@click="resource.next()"
			>
				<ChevronRight :size="16" />
			</button>
		</div>
	</div>
</template>
