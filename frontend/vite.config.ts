import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: true, // Listen on all addresses
		port: 5173,
		strictPort: true,
		hmr: {
			clientPort: 5173
		}
	},
	preview: {
		host: true,
		port: 4173
	}
});
