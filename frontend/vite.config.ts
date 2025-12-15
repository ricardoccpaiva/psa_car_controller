import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 5173,
		strictPort: true,
		hmr: {
			clientPort: 5173
		},
		// Allow all hosts in development (Docker, Proxmox, etc.)
		allowedHosts: ['*']
	}
});
