<script>
	export let indicators;
	export let getIndicatorClass;
	export let openPilotValve;
	export let closePilotValve;
	export let openActiveVent;
	export let closeActiveVent;
	export let openFillValve;
	export let closeFillValve;
	export let openDumpValve;
	export let closeDumpValve;
	export let pulseIgnitorRelay;
	export let pulseQdRelay;
	export let pulseExtraRelay;
	export let startStreaming;
	export let stopStreaming;
	export let armIgnition;
	export let startIgnitionSequence;
</script>

<div class="controls">
	<div class="grid">
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Pilot Valve</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openPilotValve}>Open</button>
				<button class="button bg-red-500" on:click={closePilotValve}>Close</button>
			</div>
			<div class="indicator {getIndicatorClass(indicators['Pilot Valve'], 'DCmotorState')}">
				{indicators['Pilot Valve']}
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Active Vent</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openActiveVent}>Open</button>
				<button class="button bg-red-500" on:click={closeActiveVent}>Close</button>
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Fill Valve</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openFillValve}>Open</button>
				<button class="button bg-red-500" on:click={closeFillValve}>Close</button>
			</div>
			<div class="indicator {getIndicatorClass(indicators['Fill Valve'], 'HanbayValveState')}">
				{indicators['Fill Valve']}
			</div>
		</div>
		<div class="flex">
			<h3 class="font-semibold text-lg mb-2">Dump Valve</h3>
			<div class="flex justify-center">
				<button class="button bg-blue-500 mr-2" on:click={openDumpValve}>Open</button>
				<button class="button bg-red-500" on:click={closeDumpValve}>Close</button>
			</div>
			<div class="indicator {getIndicatorClass(indicators['Dump Valve'], 'HanbayValveState')}">
				{indicators['Dump Valve']}
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
</div>

<style>
	.controls {
		display: flex;
		flex-direction: column;
		align-items: center;
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
		background-color: var(--blue-500);
	}

	.bg-blue-500:hover {
		background-color: var(--blue-500-hover);
	}

	.bg-red-500 {
		background-color: var(--red-500);
	}

	.bg-red-500:hover {
		background-color: var(--red-500-hover);
	}

	.bg-yellow-500 {
		background-color: var(--yellow-500);
	}

	.bg-yellow-500:hover {
		background-color: var(--yellow-500-hover);
	}

	.indicator {
		margin-top: 10px;
		padding: 5px;
		border-radius: 5px;
		color: white;
		font-weight: bold;
		text-align: center;
	}

	.indicator.button_blue {
		background-color: var(--blue-500);
	}

	.indicator.button_red {
		background-color: var(--red-500);
	}

	.indicator.button_yellow {
		background-color: var(--yellow-500);
	}

	.indicator.button_grey {
		background-color: grey;
	}
</style>
