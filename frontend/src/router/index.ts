import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useSessionStore } from '@/stores/session'

// Everything except /login is nested under AppShell (sidebar + header),
// using absolute (leading-slash) child paths -- Vue Router 4 still renders
// these through the parent's <router-view>, it just doesn't prefix the
// parent's own path onto them. Keeping every existing route's path
// unchanged (all ~25 of them, already used verbatim in router/nav.ts and
// throughout the app as router-link targets) was safer than rewriting them
// all to be nesting-relative for this restructure.
const appRoutes: RouteRecordRaw[] = [
	{ path: '/', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue') },
	{ path: '/employees', name: 'EmployeeList', component: () => import('@/pages/employees/EmployeeList.vue') },
	{
		path: '/employees/departments',
		name: 'DepartmentList',
		component: () => import('@/pages/employees/DepartmentList.vue'),
	},
	{
		path: '/employees/designations',
		name: 'DesignationList',
		component: () => import('@/pages/employees/DesignationList.vue'),
	},
	{
		path: '/employees/:employee',
		name: 'EmployeeDetail',
		component: () => import('@/pages/employees/EmployeeDetail.vue'),
		props: true,
	},
	{ path: '/documents', name: 'DocumentList', component: () => import('@/pages/documents/DocumentList.vue') },
	{
		path: '/compliance/rules',
		name: 'RuleList',
		component: () => import('@/pages/compliance/RuleList.vue'),
	},
	{
		path: '/compliance/checks',
		name: 'CheckList',
		component: () => import('@/pages/compliance/CheckList.vue'),
	},
	{
		path: '/compliance/issues',
		name: 'IssueTracker',
		component: () => import('@/pages/compliance/IssueTracker.vue'),
	},
	{
		path: '/settings/countries',
		name: 'CountrySettings',
		component: () => import('@/pages/settings/CountrySettings.vue'),
	},
	{
		path: '/settings/companies',
		name: 'CompanySettings',
		component: () => import('@/pages/settings/CompanySettings.vue'),
	},
	{
		path: '/contracts',
		name: 'Contracts',
		component: () => import('@/pages/contracts/ContractList.vue'),
	},
	{
		path: '/payroll',
		name: 'Payroll',
		component: () => import('@/pages/payroll/PayrollComplianceList.vue'),
	},
	{
		path: '/payroll/salary-slips',
		name: 'SalarySlipList',
		component: () => import('@/pages/payroll/SalarySlipList.vue'),
	},
	{
		path: '/payroll/:name',
		name: 'PayrollComplianceDetail',
		component: () => import('@/pages/payroll/PayrollComplianceDetail.vue'),
		props: true,
	},
	{
		path: '/government',
		name: 'Government',
		component: () => import('@/pages/government/SubmissionList.vue'),
	},
	{
		path: '/government/:name',
		name: 'GovernmentSubmissionDetail',
		component: () => import('@/pages/government/SubmissionDetail.vue'),
		props: true,
	},
	{
		path: '/saudi/gosi',
		name: 'Gosi',
		component: () => import('@/pages/saudi/GOSI.vue'),
	},
	{
		path: '/saudi/saudization',
		name: 'Saudization',
		component: () => import('@/pages/saudi/Saudization.vue'),
	},
	{
		path: '/saudi/compliance',
		name: 'SaudiComplianceDashboard',
		component: () => import('@/pages/saudi/ComplianceDashboard.vue'),
	},
	{
		path: '/saudi/wps',
		name: 'SaudiWPS',
		component: () => import('@/pages/saudi/WPS.vue'),
	},
	{
		path: '/saudi/leave',
		name: 'SaudiLeave',
		component: () => import('@/pages/saudi/Leave.vue'),
	},
	{
		path: '/qatar/qatarization',
		name: 'Qatarization',
		component: () => import('@/pages/qatar/Qatarization.vue'),
	},
	{
		path: '/uae/emiratisation',
		name: 'Emiratisation',
		component: () => import('@/pages/uae/Emiratisation.vue'),
	},
	{
		path: '/oman/omanisation',
		name: 'Omanisation',
		component: () => import('@/pages/oman/Omanisation.vue'),
	},
	{
		path: '/bahrain/bahrainisation',
		name: 'Bahrainisation',
		component: () => import('@/pages/bahrain/Bahrainisation.vue'),
	},
	{
		path: '/kuwait/kuwaitisation',
		name: 'Kuwaitisation',
		component: () => import('@/pages/kuwait/Kuwaitisation.vue'),
	},
	{ path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/pages/NotFound.vue') },
]

const routes: RouteRecordRaw[] = [
	{
		path: '/login',
		name: 'Login',
		component: () => import('@/pages/auth/Login.vue'),
		meta: { public: true },
	},
	{
		path: '/',
		component: () => import('@/components/layout/AppShell.vue'),
		children: appRoutes,
	},
]

const router = createRouter({
	history: createWebHistory('/gcc_hr'),
	routes,
})

// Client-side auth guard. The server-side entrypoint (gcc_hr/www/gcc_hr.py)
// no longer redirects Guests itself -- it serves the SPA shell either way,
// with boot.user = "Guest" when there's no session, so this app is the one
// that decides where a Guest lands. See DESIGN.md's "Login screen" note for
// why: a server-side redirect to Frappe's own generic /login page would
// undermine "Vue is the primary/complete UI" for the one screen users see
// most often when a session expires.
router.beforeEach((to) => {
	const session = useSessionStore()
	if (!session.ready) session.bootstrap()

	if (!session.isLoggedIn && to.meta.public !== true) {
		return { path: '/login', query: { 'redirect-to': to.fullPath } }
	}
	if (session.isLoggedIn && to.path === '/login') {
		return { path: '/' }
	}
	return true
})

export default router
