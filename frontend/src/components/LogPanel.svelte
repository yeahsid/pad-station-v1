<script>
	export let backend_logs;
	export let getLogClass;
</script>

<div class="log-container">
	<h3 class="log-heading">Logs</h3>
	<div class="log-panel">
		{#each backend_logs as log}
			<div class="log-entry {getLogClass(log)}">{log}</div>
		{/each}
	</div>
</div>

<style>
	.log-container {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.log-heading {
		margin-bottom: 10px;
		text-align: center;
	}

	.log-panel {
		background-color: #333;
		color: #fff;
		padding: 10px;
		border-radius: 5px;
		margin-right: 20px;
		width: 300px;
		max-height: 500px;
		overflow-y: auto;
		font-family: monospace;
	}

	.log-entry {
		white-space: pre-wrap;
		margin-bottom: 5px;
		padding: 5px;
		background-color: rgba(255, 255, 255, 0.1);
		border-radius: 3px;
	}

	.log-info {
		color: lightblue;
	}

	.log-warning {
		color: lightyellow;
	}

	.log-error {
		color: lightcoral;
	}
</style>
