<script setup lang="ts">
import LoadingState from './LoadingState.vue'
import EmptyState from './EmptyState.vue'

export interface DataTableColumn {
	key: string
	label: string
	align?: 'left' | 'right' | 'center'
	width?: string
}

const props = withDefaults(
	defineProps<{
		columns: DataTableColumn[]
		rows: Record<string, any>[]
		rowKey?: string
		loading?: boolean
		clickableRows?: boolean
		emptyTitle?: string
		emptyDescription?: string
	}>(),
	{
		rowKey: 'name',
		loading: false,
		clickableRows: false,
		emptyTitle: 'No records found',
		emptyDescription: '',
	},
)

const emit = defineEmits<{ 'row-click': [row: Record<string, any>] }>()

function alignClass(align?: string) {
	if (align === 'right') return 'text-right'
	if (align === 'center') return 'text-center'
	return 'text-left'
}
</script>

<template>
	<div>
		<LoadingState v-if="loading && !rows.length" />
		<EmptyState v-else-if="!rows.length" :title="emptyTitle" :description="emptyDescription" />
		<div v-else class="overflow-x-auto">
			<table class="w-full border-collapse text-[14px] leading-[20px]">
				<thead>
					<tr class="border-b border-app-border bg-app-bg">
						<th
							v-for="col in columns"
							:key="col.key"
							class="whitespace-nowrap px-4 py-2 text-[12px] font-medium uppercase leading-[16px] tracking-wide text-app-muted"
							:class="alignClass(col.align)"
							:style="col.width ? { width: col.width } : undefined"
						>
							{{ col.label }}
						</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="row in rows"
						:key="row[props.rowKey]"
						class="border-b border-app-border last:border-b-0"
						:class="clickableRows ? 'cursor-pointer hover:bg-app-bg' : ''"
						@click="clickableRows && emit('row-click', row)"
					>
						<td
							v-for="col in columns"
							:key="col.key"
							class="px-4 py-2.5 text-app-text"
							:class="alignClass(col.align)"
						>
							<slot :name="`cell-${col.key}`" :row="row">{{ row[col.key] ?? '—' }}</slot>
						</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>
</template>
