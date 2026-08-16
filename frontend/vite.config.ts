import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import path from 'path'

export default defineConfig({
	plugins: [
		frappeui({
			frontendRoute: '/gcc_hr',
		}),
		vue(),
	],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src'),
		},
	},
})
