<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { createResource, ECharts } from 'frappe-ui'
import { UserPlus, Upload, ShieldCheck, Wallet, Building2, Percent, FileSignature } from 'lucide-vue-next'
import PageHeader from '@/components/ui/PageHeader.vue'
import KpiCard from '@/components/ui/KpiCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import LoadingState from '@/components/ui/LoadingState.vue'
import ChartCard from '@/components/ui/ChartCard.vue'
import FilterBar from '@/components/ui/FilterBar.vue'
import QuickActions from '@/components/ui/QuickActions.vue'
import ShortcutList from '@/components/ui/ShortcutList.vue'
import ExpiryList from '@/components/ui/ExpiryList.vue'
import IssueList from '@/components/ui/IssueList.vue'
import CountryMetrics from '@/components/ui/CountryMetrics.vue'
import CompanySwitcher from '@/components/ui/CompanySwitcher.vue'
import { useCompanyStore } from '@/stores/company'

const companyStore = useCompanyStore()

// Must be reactive() -- visibleStatusCounts/donutEChartsOptions/the trend
// description all read filters.* and need to recompute when Apply Filters
// mutates them; a plain object's mutated properties aren't tracked by Vue.
const filters = reactive({ status: '', trendMonths: 6 })

const summary = createResource({
	url: 'gcc_hr.api.dashboard.get_summary',
	params: { company: companyStore.selectedCompany, trend_months: filters.trendMonths },
	auto: false,
})

const latestPayrollCheck = createResource({
	url: 'frappe.client.get_list',
	params: {
		doctype: 'Payroll Compliance Check',
		fields: ['name', 'status', 'check_date'],
		filters: {},
		order_by: 'check_date desc',
		limit_page_length: 1,
	},
	auto: false,
})

function reloadForCompany(company: string, trendMonths: number) {
	if (!company) return
	summary.update({ params: { company, trend_months: trendMonths } })
	summary.reload()
	latestPayrollCheck.update({
		params: {
			doctype: 'Payroll Compliance Check',
			fields: ['name', 'status', 'check_date'],
			filters: { company },
			order_by: 'check_date desc',
			limit_page_length: 1,
		},
	})
	latestPayrollCheck.reload()
}

watch(() => companyStore.selectedCompany, (company) => reloadForCompany(company, filters.trendMonths), { immediate: true })

function applyFilters(next: { status: string; trendMonths: number }) {
	filters.status = next.status
	filters.trendMonths = next.trendMonths
	reloadForCompany(companyStore.selectedCompany, next.trendMonths)
}

const latestPayrollStatus = computed(() => latestPayrollCheck.data?.[0]?.status || 'No data')

const visibleStatusCounts = computed(() => {
	if (!summary.data) return {}
	if (!filters.status) return summary.data.status_counts
	return { [filters.status]: summary.data.status_counts[filters.status] }
})

function scoreTone(score: number): 'success' | 'warning' | 'danger' {
	if (score >= 75) return 'success'
	if (score >= 50) return 'warning'
	return 'danger'
}

const STATUS_COLORS: Record<string, string> = {
	Compliant: '#28A745',
	Warning: '#F59E0B',
	Critical: '#E5484D',
	Blocked: '#9CA3AF',
}

// frappe-ui's DonutChart wrapper has no way to get a clean ring with neither
// its own legend (ugly, paginated with 4 categories) nor inline slice labels
// (rendered as an overlapping mess of leader lines when several slices are
// 0%/tiny) -- so this bypasses DonutChart and builds a raw ECharts pie
// option instead: a plain ring, no labels, `itemStyle.color` set per-datum
// so color stays bound to its category regardless of any internal sort.
const donutEChartsOptions = computed(() => {
	const counts: Record<string, number> = visibleStatusCounts.value || {}
	const order = ['Compliant', 'Warning', 'Critical', 'Blocked']
	const data = order
		.filter((status) => counts[status] !== undefined)
		.map((status) => ({ name: status, value: counts[status], itemStyle: { color: STATUS_COLORS[status] } }))
	return {
		tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
		series: [
			{
				type: 'pie',
				radius: ['55%', '80%'],
				center: ['50%', '50%'],
				label: { show: false },
				labelLine: { show: false },
				emphasis: { scale: true, scaleSize: 4 },
				data,
			},
		],
	}
})

const hasStatusData = computed(() =>
	Object.values(visibleStatusCounts.value || {}).some((n) => Number(n) > 0),
)

// Proportional-bar breakdown shown next to the donut, matching the reference
// image's "dot + label + bar + percentage(count)" rows -- ECharts' own
// legend can't produce this layout.
const statusBreakdown = computed(() => {
	const counts = visibleStatusCounts.value || {}
	const total = Object.values(counts).reduce((sum: number, n) => sum + (Number(n) || 0), 0)
	return Object.entries(counts).map(([status, count]) => ({
		status,
		count: count as number,
		percentage: total ? Math.round(((count as number) / total) * 1000) / 10 : 0,
		color: STATUS_COLORS[status] || '#9CA3AF',
	}))
})

const trendConfig = computed(() => ({
	title: '',
	data: summary.data?.compliance_trend || [],
	xAxis: { key: 'month', type: 'category' as const },
	yAxis: { title: 'Score %', yMin: 0, yMax: 100 },
	series: [{ name: 'average_score', type: 'line' as const, color: '#2490EF' }],
}))

const quickActions = [
	{ label: 'New Employee', href: '/app/employee/new', icon: UserPlus },
	{ label: 'Upload Document', href: '/gcc_hr/documents', icon: Upload },
	{ label: 'Run Compliance Check', href: '/gcc_hr/compliance/checks', icon: ShieldCheck },
	{ label: 'Payroll Compliance Check', href: '/gcc_hr/payroll', icon: Wallet },
]

const shortcuts = computed(() => {
	if (companyStore.selectedCountry !== 'Saudi Arabia') return []
	return [
		{ label: 'Saudi Dashboard', route: '/saudi/compliance', icon: ShieldCheck },
		{ label: 'Saudization Simulator', route: '/saudi/saudization', icon: Percent },
		{ label: 'GOSI Contributions', route: '/saudi/gosi', icon: Building2 },
		{ label: 'Government Filing', route: '/government', icon: FileSignature },
	]
})
</script>

<template>
	<div>
		<PageHeader title="Command Center" description="Company overview across employees, documents, and compliance.">
			<template #action>
				<CompanySwitcher />
			</template>
		</PageHeader>

		<div class="p-6">
			<LoadingState v-if="!companyStore.ready || (summary.loading && !summary.data)" />

			<div v-else-if="!companyStore.selectedCompany" class="py-12 text-center text-[13px] text-app-muted">
				No company configured yet -- add one under Settings &gt; Companies to see the Command Center.
			</div>

			<div v-else-if="summary.data" class="grid grid-cols-1 gap-4 lg:grid-cols-3">
				<div class="space-y-4 lg:col-span-2">
					<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-5">
						<KpiCard label="Total Employees" :value="summary.data.total_employees" />
						<KpiCard
							label="Compliance Score"
							:value="`${summary.data.average_score}%`"
							:tone="scoreTone(summary.data.average_score)"
							:hint="summary.data.average_score >= 75 ? 'Good' : 'Needs attention'"
						/>
						<KpiCard
							label="Critical Issues"
							:value="summary.data.status_counts.Critical"
							:tone="summary.data.status_counts.Critical ? 'danger' : 'neutral'"
							hint="Needs action"
						/>
						<KpiCard label="Documents Expiring" :value="summary.data.documents_expiring_soon" tone="warning" hint="Next 30 days" />
						<KpiCard
							label="Payroll Status"
							:value="latestPayrollStatus"
							:tone="latestPayrollStatus === 'Passed' ? 'success' : latestPayrollStatus === 'No data' ? 'neutral' : 'warning'"
						/>
					</div>

					<div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
						<SectionCard title="Employee Compliance Status">
							<div class="flex flex-col gap-4 sm:flex-row sm:items-center">
								<div v-if="hasStatusData" class="w-full sm:w-2/5">
									<ECharts :options="donutEChartsOptions" class="h-56 w-full min-w-0" />
								</div>
								<div class="w-full" :class="hasStatusData ? 'space-y-2.5 sm:w-3/5' : 'space-y-2.5'">
									<div v-for="row in statusBreakdown" :key="row.status">
										<div class="mb-1 flex items-center justify-between text-[12px] leading-[16px]">
											<span class="flex items-center gap-1.5 text-app-text">
												<span class="h-2 w-2 rounded-full" :style="{ backgroundColor: row.color }" />
												{{ row.status }}
											</span>
											<span class="text-app-muted">{{ row.percentage }}% ({{ row.count }})</span>
										</div>
										<div class="h-1.5 overflow-hidden rounded-full bg-app-bg">
											<div
												class="h-full rounded-full"
												:style="{ width: `${row.percentage}%`, backgroundColor: row.color }"
											/>
										</div>
									</div>
								</div>
							</div>
						</SectionCard>

						<ChartCard
							title="Compliance Trend"
							:description="`Last ${filters.trendMonths} months`"
							type="axis"
							:config="trendConfig"
						/>
					</div>

					<CountryMetrics :company="companyStore.selectedCompany" :country="companyStore.selectedCountry" />

					<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
						<ExpiryList :rows="summary.data.documents_expiring_by_type" />
						<IssueList :issues="summary.data.recent_critical_issues" />
					</div>
				</div>

				<div class="space-y-4">
					<FilterBar :status="filters.status" :trend-months="filters.trendMonths" @apply="applyFilters" />
					<QuickActions :actions="quickActions" />
					<ShortcutList :shortcuts="shortcuts" />
				</div>
			</div>
		</div>
	</div>
</template>
