<script>
	export let name;

	let message = "";
	const backendUrl = "http://localhost:8000";
	const socket = new WebSocket(`${backendUrl.replace("http", "ws")}/ws/data`);

	async function fetchMessage() {
		const response = await fetch(`${backendUrl}/`);
		const data = await response.json();
		message = data.message;
	}

	socket.onopen = function(event) {
		console.log("WebSocket connection opened");
	};

	socket.onmessage = function(event) {
		const data = JSON.parse(event.data);
		console.log("Received data:", data);
		// Update your frontend with the received data
	};

	socket.onclose = function(event) {
		console.log("WebSocket connection closed");
	};

	socket.onerror = function(error) {
		console.log("WebSocket error:", error);
	};

	async function sendRequest(endpoint) {
		const response = await fetch(`${backendUrl}${endpoint}`, {
			method: "POST",
		});
		const data = await response.json();
		console.log(data);
	}

	function openPilotValve() {
		sendRequest("/pilot-valve/open");
	}

	function closePilotValve() {
		sendRequest("/pilot-valve/close");
	}

	function openActiveVent() {
		sendRequest("/active-vent/open");
	}

	function closeActiveVent() {
		sendRequest("/active-vent/close");
	}

	function openFillValve() {
		sendRequest("/fill-valve/open");
	}

	function closeFillValve() {
		sendRequest("/fill-valve/close");
	}

	function openDumpValve() {
		sendRequest("/dump-valve/open");
	}

	function closeDumpValve() {
		sendRequest("/dump-valve/close");
	}

	function pulseIgnitorRelay() {
		sendRequest("/relay/ignitor/pulse");
	}

	function pulseQdRelay() {
		sendRequest("/relay/qd/pulse");
	}

	function pulseExtraRelay() {
		sendRequest("/relay/extra/pulse");
	}

	function startStreaming() {
		sendRequest("/streaming/start");
	}

	function stopStreaming() {
		sendRequest("/streaming/stop");
	}

	fetchMessage();
</script>

<main>
	<h1>Hello {name}!</h1>
	<p>Visit the <a href="https://svelte.dev/tutorial">Svelte tutorial</a> to learn how to build Svelte apps.</p>
	<p>{message}</p>
	<div>
		<h2>Control Panel</h2>
		<button on:click={openPilotValve}>Open Pilot Valve</button>
		<button on:click={closePilotValve}>Close Pilot Valve</button>
		<button on:click={openActiveVent}>Open Active Vent</button>
		<button on:click={closeActiveVent}>Close Active Vent</button>
		<button on:click={openFillValve}>Open Fill Valve</button>
		<button on:click={closeFillValve}>Close Fill Valve</button>
		<button on:click={openDumpValve}>Open Dump Valve</button>
		<button on:click={closeDumpValve}>Close Dump Valve</button>
		<button on:click={pulseIgnitorRelay}>Pulse Ignitor Relay</button>
		<button on:click={pulseQdRelay}>Pulse QD Relay</button>
		<button on:click={pulseExtraRelay}>Pulse Extra Relay</button>
		<button on:click={startStreaming}>Start Streaming</button>
		<button on:click={stopStreaming}>Stop Streaming</button>
	</div>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}

	button {
		margin: 0.5em;
		padding: 0.5em 1em;
		font-size: 1em;
	}
</style>