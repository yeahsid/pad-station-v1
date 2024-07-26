

import * as Sentry from "@sentry/svelte";
import './app.css';

import App from './App.svelte';
Sentry.init({
	dsn: "http://0b27760dfd69e45f67fbe80fd94b6b2d@server.goblin-decibel.ts.net:9000/2",
	integrations: [
		Sentry.browserTracingIntegration(),
		Sentry.replayIntegration(),
	],

	// Set tracesSampleRate to 1.0 to capture 100%
	// of transactions for tracing.
	// We recommend adjusting this value in production
	tracesSampleRate: 1.0,

	// Set `tracePropagationTargets` to control for which URLs trace propagation should be enabled
	tracePropagationTargets: ["localhost", "server.goblin-decibel.ts.net:3000"],

	// Capture Replay for 10% of all sessions,
	// plus 100% of sessions with an error
	replaysSessionSampleRate: 0.1,
	replaysOnErrorSampleRate: 1.0,
});


const app = new App({
	target: document.getElementById('app')!,
});

export default app;
