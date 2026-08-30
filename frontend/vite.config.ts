import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 3000,
		host: '0.0.0.0',
		// File watching must use polling: the app runs inside a container
		// (podman) with the source bind-mounted from the host, and the native
		// inotify watcher does not reliably see host-side changes on some setups.
		watch: {
			usePolling: true,
			interval: 300
		}
	}
});
