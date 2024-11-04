<script>
	let message = "";
	const backendUrl = "http://localhost:8000";
	const socket = new WebSocket(`${backendUrl.replace("http", "ws")}/ws/data`);
	let indicators = {};

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
		indicators = data; // Update indicators with received data
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

	function armIgnition() {
		sendRequest("/pilot-valve/arm-ignition");
	}

	function startIgnitionSequence() {
		sendRequest("/pilot-valve/start-ignition-sequence");
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

<style>
	main {
		background-color: #f9f9f9;
		border-radius: 10px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		margin: auto;
		padding: 20px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	h2 {
		color: #333;
	}

	h3 {
		color: #555;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20px;
	}

	.flex {
		display: flex;
		flex-direction: column;
	}

	.button {
		border-radius: 8px;
		padding: 10px 20px;
		color: white;
		font-weight: bold;
		border: none;
		cursor: pointer;
		transition: background-color 0.3s, transform 0.3s;
	}

	.button:hover {
		transform: scale(1.05);
	}

	.bg-blue-500 {
		background-color: #2890ff; /* Brighter blue */
	}

	.bg-blue-500:hover {
		background-color: #0056b3; /* Darker blue hover */
	}

	.bg-red-500 {
		background-color: #da644a; /* Brighter red */
	}

	.bg-red-500:hover {
		background-color: #C0392B; /* Darker red hover */
	}

	.bg-yellow-500 {
		background-color: #FFC300; /* Brighter yellow */
	}

	.bg-yellow-500:hover {
		background-color: #E6B700; /* Darker yellow hover */
	}

	.indicator {
		margin-top: 10px;
		padding: 5px;
		border-radius: 5px;
		color: white;
		font-weight: bold;
	}
	.indicator.open {
		background-color: green;
	}
	.indicator.closed {
		background-color: red;
	}
</style>

<main class="text-center p-8">
	<h2 class="text-3xl font-bold mb-6">Pad Station Control Panel</h2>
	<div class="grid">
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Pilot Valve</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openPilotValve}>Open</button>
				<button class="button bg-red-500" on:click={closePilotValve}>Close</button>
			</div>
			<div class="indicator {indicators['pilot_valve'] === 'OPEN' ? 'open' : 'closed'}">
				{indicators['pilot_valve']}
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Active Vent</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openActiveVent}>Open</button>
				<button class="button bg-red-500" on:click={closeActiveVent}>Close</button>
			</div>
			<div class="indicator {indicators['active_vent'] === 'OPEN' ? 'open' : 'closed'}">
				{indicators['active_vent']}
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Fill Valve</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openFillValve}>Open</button>
				<button class="button bg-red-500" on:click={closeFillValve}>Close</button>
			</div>
			<div class="indicator {indicators['fill_valve'] === 'OPEN' ? 'open' : 'closed'}">
				{indicators['fill_valve']}
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Dump Valve</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openDumpValve}>Open</button>
				<button class="button bg-red-500" on:click={closeDumpValve}>Close</button>
			</div>
			<div class="indicator {indicators['dump_valve'] === 'OPEN' ? 'open' : 'closed'}">
				{indicators['dump_valve']}
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Relays</h3>
			<div class="flex justify-center">
				<button class="button bg-yellow-500 mr-2" on:click={pulseIgnitorRelay}>Pulse Ignitor</button>
				<button class="button bg-yellow-500 mr-2" on:click={pulseQdRelay}>Pulse QD</button>
				<button class="button bg-yellow-500" on:click={pulseExtraRelay}>Pulse Extra</button>
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Streaming</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={startStreaming}>Start Streaming</button>
				<button class="button bg-red-500" on:click={stopStreaming}>Stop Streaming</button>
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Ignition Sequence</h3>
			<div class="flex justify-center">
				<button class="button bg-yellow-500 mr-2" on:click={armIgnition}>Arm Ignition</button>
				<button class="button bg-red-500" on:click={startIgnitionSequence}>Start Ignition Sequence</button>
			</div>
		</div>
	</div>
</main>
