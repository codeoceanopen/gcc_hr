import { defineStore } from 'pinia'
import { call } from 'frappe-ui'

declare global {
	interface Window {
		user?: string
		full_name?: string
		user_image?: string | null
		roles?: string[]
		site_name?: string
	}
}

function cleanWindowValue(value?: string | null): string {
	if (!value || value.startsWith('{{')) return ''
	return value
}

export const useSessionStore = defineStore('session', {
	state: () => ({
		user: '' as string,
		fullName: '' as string,
		userImage: null as string | null,
		roles: [] as string[],
		siteName: '' as string,
		ready: false,
	}),
	actions: {
		bootstrap() {
			this.user = cleanWindowValue(window.user)
			this.fullName = cleanWindowValue(window.full_name) || this.user
			this.userImage = window.user_image ?? null
			this.roles = Array.isArray(window.roles) ? window.roles : []
			this.siteName = cleanWindowValue(window.site_name)
			this.ready = true
		},
		hasRole(role: string): boolean {
			return this.roles.includes(role)
		},
		hasAnyRole(roles: string[]): boolean {
			return roles.some((role) => this.roles.includes(role))
		},
		async logout() {
			await call('logout')
			window.location.href = '/login'
		},
	},
	getters: {
		isLoggedIn: (state) => Boolean(state.user) && state.user !== 'Guest',
		initials: (state) => (state.fullName || state.user || '?').slice(0, 2).toUpperCase(),
		isAdmin: (state) => state.roles.includes('System Manager') || state.roles.includes('GCC HR Administrator'),
	},
})
