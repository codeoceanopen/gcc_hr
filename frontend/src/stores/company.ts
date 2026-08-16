import { defineStore } from 'pinia'
import { createListResource } from 'frappe-ui'

// New persistence pattern (no precedent in stores/session.ts, which never
// persists anything) -- deliberately remembers the operator's last-selected
// company across reloads, since re-picking it every page load would defeat
// the point of a global "which company am I managing" context.
const STORAGE_KEY = 'gcc_hr:selectedCompany'

export interface CompanyRow {
	company: string
	country: string
}

export const useCompanyStore = defineStore('company', {
	state: () => ({
		companies: [] as CompanyRow[],
		selectedCompany: '' as string,
		ready: false,
	}),
	actions: {
		bootstrap() {
			if (this.ready) return
			createListResource({
				doctype: 'GCC HR Company Settings',
				fields: ['company', 'country'],
				pageLength: 100,
				auto: true,
				onSuccess: (data: CompanyRow[]) => {
					this.companies = data || []
					const stored = window.localStorage.getItem(STORAGE_KEY)
					const storedIsValid = Boolean(stored) && this.companies.some((c) => c.company === stored)
					this.selectedCompany = storedIsValid ? (stored as string) : this.companies[0]?.company || ''
					this.ready = true
				},
			})
		},
		selectCompany(company: string) {
			this.selectedCompany = company
			window.localStorage.setItem(STORAGE_KEY, company)
		},
	},
	getters: {
		selectedCountry: (state): string =>
			state.companies.find((c) => c.company === state.selectedCompany)?.country || '',
	},
})
