<script>
	export let indicators;
</script>

<div class="sensors-panel">
	<div class="sensor">
		<h4>Supply PT (Bar)</h4>
		<p class="sensor-value">{indicators['Supply Pressure Transducer']}</p>
	</div>
	<div class="sensor">
		<h4>Fill PT (Bar)</h4>
		<p class="sensor-value">{indicators['Fill Pressure Transducer']}</p>
	</div>
	<div class="sensor">
		<h4>Load Cell (N)</h4>
		<p class="sensor-value">{indicators['Load Cell']}</p>
	</div>
	<div class="sensor">
		<h4>External PT 1 (Bar)</h4>
		<p class="sensor-value">{indicators['External Pressure Transducer 1']}</p>
	</div>
	<div class="sensor">
		<h4>External PT 2 (Bar)</h4>
		<p class="sensor-value">{indicators['External Pressure Transducer 2']}</p>
	</div>
	<div class="sensor">
		<h4>Thermocouple (C)</h4>
		<p class="sensor-value">{indicators['Thermocouple']}</p>
	</div>
</div>

<style>
	.sensors-panel {
		display: flex;
		justify-content: space-around;
		margin-top: 20px;
	}

	.sensor {
		background-color: #f0f0f0;
		padding: 10px;
		border-radius: 5px;
		text-align: center;
		width: 150px;
	}

	.sensor h4 {
		margin-bottom: 5px;
		font-size: 14px;
	}

	.sensor-value {
		font-size: 16px;
		font-weight: bold;
		text-align: bottom; /* Align the numbers to the right */
	}
</style>
