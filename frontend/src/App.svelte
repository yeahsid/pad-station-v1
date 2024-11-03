<script>
	export let name;

	let message = "";
	const socket = new WebSocket("ws://localhost:8000/ws/data");

	async function fetchMessage() {
		const response = await fetch("http://localhost:8000/");
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

  fetchMessage();
</script>



<main>
	<h1>Hello {name}!</h1>
	<p>Visit the <a href="https://svelte.dev/tutorial">Svelte tutorial</a> to learn how to build Svelte apps.</p>
	<p>{message}</p>
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
</style>