<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { FormControl, Button } from 'frappe-ui'

const route = useRoute()

const form = reactive({ usr: '', pwd: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
	if (!form.usr || !form.pwd) {
		error.value = 'Enter your email/username and password.'
		return
	}
	loading.value = true
	error.value = ''
	try {
		const res = await fetch('/api/method/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded', Accept: 'application/json' },
			body: new URLSearchParams({ usr: form.usr, pwd: form.pwd }),
		})
		if (!res.ok) {
			const data = await res.json().catch(() => ({}))
			throw new Error(data.message || data._server_messages || 'Invalid email or password.')
		}
		// Hard navigation, not client-side routing -- window.user/full_name/
		// roles are plain globals set once at page render time (see
		// gcc_hr/www/gcc_hr.py), so only a fresh server-rendered page picks
		// up the newly-authenticated session. Same pattern the session
		// store's own logout() action already uses in reverse.
		const redirectTo = (route.query['redirect-to'] as string) || '/gcc_hr'
		window.location.href = redirectTo
	} catch (err) {
		error.value = 'Invalid email or password.'
	} finally {
		loading.value = false
	}
}
</script>

<template>
	<div class="flex min-h-screen items-center justify-center bg-app-bg px-4">
		<div class="w-full max-w-[360px]">
			<div class="mb-6 text-center">
				<p class="text-[20px] font-semibold leading-[24px] text-app-text">GCC HR</p>
				<p class="mt-1 text-[13px] leading-[16px] text-app-muted">HR Localization &amp; Compliance</p>
			</div>

			<div class="rounded-app-md border border-app-border bg-app-surface p-6">
				<h1 class="text-[16px] font-semibold leading-[20px] text-app-text">Sign in</h1>
				<p class="mt-1 text-[13px] leading-[16px] text-app-muted">Use your GCC HR account to continue.</p>

				<form class="mt-5 space-y-4" @submit.prevent="submit">
					<FormControl v-model="form.usr" label="Email" type="text" variant="outline" autocomplete="username" required />
					<FormControl v-model="form.pwd" label="Password" type="password" variant="outline" autocomplete="current-password" required />

					<p v-if="error" class="rounded-app-sm bg-app-danger-surface px-3 py-2 text-[13px] leading-[16px] text-app-danger">
						{{ error }}
					</p>

					<Button theme="blue" variant="solid" class="w-full justify-center" :loading="loading" @click="submit">
						Sign in
					</Button>
				</form>
			</div>
		</div>
	</div>
</template>
