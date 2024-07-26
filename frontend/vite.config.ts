import { sentryVitePlugin } from "@sentry/vite-plugin";
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import compression from 'vite-plugin-compression';


// https://vitejs.dev/config/
export default defineConfig({
    plugins: [svelte(), compression(), sentryVitePlugin({
        org: "monash-hpr",
        project: "pad-station",
        url: "http://server.goblin-decibel.ts.net:9000"
    })],

    build: {
        sourcemap: true
    }
});