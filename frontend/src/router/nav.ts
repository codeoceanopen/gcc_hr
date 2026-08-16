// Single source of nav items -- both the Sidebar and the router read from
// this list. Items with a `comingInPhase` are shown (so the full Command
// Center structure the product brief describes is visible) but route to a
// placeholder rather than fake functionality -- Phase 1 only ships Core.
export const CURRENT_PHASE = 10

export interface NavItem {
	label: string
	route: string
	icon: string
	comingInPhase?: number
}

export interface NavSection {
	label: string
	items: NavItem[]
	// Exact HR Country Settings name -- when set, Sidebar.vue only shows this
	// section while the globally-selected company's country matches. Country
	// visibility alone is not the security boundary (the backend enforces
	// that independently, see gcc_hr_company_settings.enforce_company_country)
	// -- this is purely to avoid showing a company irrelevant modules.
	country?: string
	// Rendered fixed at the sidebar's bottom, separated by a border, instead
	// of scrolling with the rest -- matches the reference design's footer-
	// pinned Settings section.
	pinned?: boolean
}

export const NAV_SECTIONS: NavSection[] = [
	{
		label: 'Overview',
		items: [{ label: 'Command Center', route: '/', icon: 'LayoutDashboard' }],
	},
	{
		label: 'Employees',
		items: [
			{ label: 'Compliance Profiles', route: '/employees', icon: 'Users' },
			{ label: 'Departments', route: '/employees/departments', icon: 'Building2' },
			{ label: 'Designations', route: '/employees/designations', icon: 'Percent' },
		],
	},
	{
		label: 'Documents',
		items: [{ label: 'Compliance Documents', route: '/documents', icon: 'FileText' }],
	},
	{
		label: 'Compliance',
		items: [
			{ label: 'Compliance Checks', route: '/compliance/checks', icon: 'ShieldCheck' },
			{ label: 'Compliance Rules', route: '/compliance/rules', icon: 'ListChecks' },
			{ label: 'Issue Tracker', route: '/compliance/issues', icon: 'ListChecks' },
		],
	},
	{
		label: 'Contracts',
		items: [{ label: 'Employment Contracts', route: '/contracts', icon: 'FileSignature' }],
	},
	{
		label: 'Payroll',
		items: [
			{ label: 'Payroll Compliance', route: '/payroll', icon: 'Wallet' },
			{ label: 'Salary Slips', route: '/payroll/salary-slips', icon: 'FileText' },
		],
	},
	{
		label: 'Government',
		items: [{ label: 'Government Integration', route: '/government', icon: 'Landmark' }],
	},
	{
		label: 'Saudi Arabia',
		country: 'Saudi Arabia',
		items: [
			{ label: 'Compliance Dashboard', route: '/saudi/compliance', icon: 'ShieldCheck' },
			{ label: 'GOSI', route: '/saudi/gosi', icon: 'Building2' },
			{ label: 'Saudization', route: '/saudi/saudization', icon: 'Percent' },
			{ label: 'Leave', route: '/saudi/leave', icon: 'FileSignature' },
			{ label: 'WPS / Government Filing', route: '/saudi/wps', icon: 'Landmark' },
		],
	},
	{
		label: 'Qatar',
		country: 'Qatar',
		items: [{ label: 'Qatarization', route: '/qatar/qatarization', icon: 'Percent' }],
	},
	{
		label: 'UAE',
		country: 'United Arab Emirates',
		items: [{ label: 'Emiratisation', route: '/uae/emiratisation', icon: 'Percent' }],
	},
	{
		label: 'Oman',
		country: 'Oman',
		items: [{ label: 'Omanisation', route: '/oman/omanisation', icon: 'Percent' }],
	},
	{
		label: 'Bahrain',
		country: 'Bahrain',
		items: [{ label: 'Bahrainisation', route: '/bahrain/bahrainisation', icon: 'Percent' }],
	},
	{
		label: 'Kuwait',
		country: 'Kuwait',
		items: [{ label: 'Kuwaitisation', route: '/kuwait/kuwaitisation', icon: 'Percent' }],
	},
	{
		label: 'Settings',
		pinned: true,
		items: [
			{ label: 'Countries', route: '/settings/countries', icon: 'Globe' },
			{ label: 'Companies', route: '/settings/companies', icon: 'Building' },
		],
	},
]
