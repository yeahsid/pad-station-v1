import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import compression from 'vite-plugin-compression';


// https://vitejs.dev/config/
export default defineConfig({
	plugins: [svelte() , compression()],
});
