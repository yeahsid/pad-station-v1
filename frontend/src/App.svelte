<script>
	import LogPanel from './components/LogPanel.svelte';
	import Controls from './components/Controls.svelte';
	import SensorsPanel from './components/SensorsPanel.svelte'; // Import the new component

	let message = "";
	let backendUrl;

	if (window.location.hostname === "localhost") {
        backendUrl = "http://localhost:8000";
    } else {
        backendUrl = "http://padstation-prod.goblin-decibel.ts.net:8000";
    }

	const socket = new WebSocket(`${backendUrl.replace("http", "ws")}/ws/data`);
	let indicators = {};
	let isStreaming = false; // Initialize the streaming state

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

	async function armIgnition() {
		try {
			const response = await fetch(`${backendUrl}/ignition/arm`, { method: 'POST' });
			const data = await response.json();
			ignitionArmed = data.armed;  // Update the armed status
			console.log(data.status);
		} catch (error) {
			console.error('Error:', error);
		}
	}

	function startIgnitionSequence() {
		sendRequest("/ignition/start");
	}

	function abortIgnition() {
		sendRequest("/ignition/abort");
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

	async function startStreaming() {
		try {
			const response = await fetch(`${backendUrl}/streaming/start`, { method: "POST" });
			const data = await response.json();
			console.log(data);
			if (data.status === "Streaming started") {
				isStreaming = true; // Update the streaming state
			}
		} catch (error) {
			console.error('Error starting streaming:', error);
		}
	}

	async function stopStreaming() {
		try {
			const response = await fetch(`${backendUrl}/streaming/stop`, { method: "POST" });
			const data = await response.json();
			console.log(data);
			if (data.status === "Streaming stopped") {
				isStreaming = false; // Update the streaming state
			}
		} catch (error) {
			console.error('Error stopping streaming:', error);
		}
	}

	fetchMessage();

	function getIndicatorClass(state, type) {
		if (type === 'BinaryPosition') {
			return state === 'OPEN' ? 'button_blue' : 'button_red';
		} else if (type === 'DCmotorState') {
			if (state === 'OPEN') {
				return 'button_blue';
			} else if (state === 'CLOSE') {
				return 'button_red';
			} else {
				return 'button_yellow';
			}
		} else if (type === 'HanbayValveState') {
			if (state === 'IN_POSITION') {
				return 'button_blue';
			} else if (state === 'MOVING') {
				return 'button_yellow';
			} else if (state === 'STALLED') {
				return 'button_red';
			} else {
				return 'button_grey';
			}
		}
		return 'yellow';
	}

	let backend_logs = [];

	const logSocket = new WebSocket(`${backendUrl.replace("http", "ws")}/ws/logs`);

	logSocket.onmessage = function(event) {
		const log = event.data;
		backend_logs = [...backend_logs, log].slice(-10); // Keep only the last 10 logs
	};

	logSocket.onerror = function(error) {
		console.error("WebSocket error:", error);
	};

	function getLogClass(log) {
		if (log.startsWith("INFO")) {
			return "log-info";
		} else if (log.startsWith("WARNING")) {
			return "log-warning";
		} else if (log.startsWith("ERROR")) {
			return "log-error";
		}
		return "";
	}

	let ignitionArmed = false;

</script>

<style>
	:root {
		--blue-500: #2890ff;
		--blue-500-hover: #0056b3;
		--red-500: #da644a;
		--red-500-hover: #C0392B;
		--yellow-500: #FFC300;
		--yellow-500-hover: #E6B700;
		--green-500: #2ecc71;
		--green-500-hover: #27ae60;
	}

	main {
		background-color: #f9f9f9;
		border-radius: 10px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		margin: auto;
		padding: 20px;
		display: flex;
		flex-direction: row;
		align-items: flex-start;
		justify-content: center;
	}

	.main-container {
		display: flex;
	}

	.vertical-container {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.title {
		text-align: center;
		width: 100%;
	}
</style>

<h2 class="text-3xl font-bold mb-6 title">Pad Station Control Panel</h2>
<main class="text-center p-8">
	<div class="main-container">
		<LogPanel {backend_logs} {getLogClass} />
		<div class="vertical-container">
			<SensorsPanel {indicators} /> <!-- Move the SensorsPanel component to the top -->
			<Controls
				{indicators}
				{getIndicatorClass}
				{openFillValve}
				{closeFillValve}
				{openDumpValve}
				{closeDumpValve}
				{openPilotValve}
				{closePilotValve}
				{openActiveVent}
				{closeActiveVent}
				{pulseIgnitorRelay}
				{pulseQdRelay}
				{pulseExtraRelay}
				{startStreaming}
				{stopStreaming}
				{armIgnition}
				{startIgnitionSequence}
				{abortIgnition}
				{ignitionArmed}
				{isStreaming}
			/>
		</div>
	</div>
</main>
