type Tone = 'success' | 'warning' | 'danger' | 'neutral'

export function complianceTone(status: string): Tone {
	return (
		({ Compliant: 'success', Warning: 'warning', Critical: 'danger', Blocked: 'danger' } as Record<string, Tone>)[
			status
		] || 'neutral'
	)
}

export function documentStatusTone(status: string): Tone {
	return (
		({ Valid: 'success', 'Expiring Soon': 'warning', Expired: 'danger' } as Record<string, Tone>)[status] ||
		'neutral'
	)
}

export function severityTone(severity: string): Tone {
	return (
		({ Info: 'neutral', Warning: 'warning', Critical: 'danger', Blocking: 'danger' } as Record<string, Tone>)[
			severity
		] || 'neutral'
	)
}

export function relativeDays(dateStr: string): string {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	const today = new Date()
	date.setHours(0, 0, 0, 0)
	today.setHours(0, 0, 0, 0)
	const diffDays = Math.round((date.getTime() - today.getTime()) / 86400000)
	if (diffDays === 0) return 'Today'
	if (diffDays === 1) return 'Tomorrow'
	if (diffDays === -1) return 'Yesterday'
	if (diffDays > 0) return `In ${diffDays} day(s)`
	return `${Math.abs(diffDays)} day(s) ago`
}

export function governmentSubmissionTone(status: string): Tone {
	return (
		({
			Draft: 'neutral',
			Generated: 'neutral',
			Validated: 'warning',
			'Ready for Submission': 'warning',
			Submitted: 'warning',
			'Response Uploaded': 'warning',
			Completed: 'success',
		} as Record<string, Tone>)[status] || 'neutral'
	)
}
