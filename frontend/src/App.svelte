<script lang="ts">
  import {
    Heading,
    P,
    Badge,
    Indicator,
    Button,
    Select,
  } from "flowbite-svelte";
  import { onMount } from "svelte";

/*
importing various components and functions from flowbite-svelte and svelte
these are used to create the user interface. 
'onmount' is a lifecycle function that runs after the component is first rendered 
*/

//an array of objects representing possible valve actions 
  const actions: { value: string; name: string }[] = [
    {
      value: "open",
      name: "Open",
    },
    {
      value: "closed",
      name: "Close",
    },
  ];

//typescript union types that define possible connection states and valve states
  type TConnectionStatus = "Connected" | "Error" | "Unknown";
  type TValveState = "Open" | "Close" | "Error" | "Unknown";
//defines a set of possible colour values 
  type TColorType =
    | "green"
    | "red"
    | "dark"
    | "none"
    | "yellow"
    | "indigo"
    | "purple"
    | "pink"
    | "blue"
    | "primary"
    | undefined;

//base url is for API calls to get the data from the backend 
  const BASE_URL = "http://padstation-dev.local:8000";

//maps valve states to colour types 
  const colorMap: Record<TConnectionStatus | TValveState, TColorType> = {
    Connected: "green",
    Error: "red",
    Unknown: "dark",
    Open: "green",
    Close: "red",
  };

//variables to store states and data points 
  let supplyPt: string;
  let enginePt: string;
  let tankPt: string;
  let chamberPt: string;
  let engineTc: string;
  let engineState: TValveState = "Unknown";
  let supplyState: TValveState = "Unknown";
  let tankState: TValveState = "Unknown";
  let chamberState: TValveState = "Unknown";
  let engineTcState: TValveState = "Unknown";
  let selectedEngineOption: string | undefined;
  let selectedSupplyOption: string | undefined;
  let selectedTankOption: string | undefined;
  let selectedChamberOption: string | undefined;
  let selectedEngineTOption: string | undefined;
  let engineSseStatus: TConnectionStatus = "Unknown";
  let supplySseStatus: TConnectionStatus = "Unknown";
  let tankSseStatus: TConnectionStatus = "Unknown";
  let chamberSseStatus: TConnectionStatus = "Unknown";
  let engineTcSseStatus: TConnectionStatus = "Unknown";

  // New state variable for logging status
  let isLogging = false;

//The onMount function sets up EventSource connections to receive real-time updates
  onMount(() => {
    //pressure data stream
    const enginePressureSse = new EventSource(
      `${BASE_URL}/pressure/tank_bottom/datastream`
    );

    //pressure data stream
    const supplyPressureSse = new EventSource(
      `${BASE_URL}/pressure/supply/datastream`
    );

    //pressure data stream
    const tankPressureSse = new EventSource(
      `${BASE_URL}/pressure/tank_top/datastream`
    );

    //pressure data stream
    const chamberPressureSse = new EventSource(
      `${BASE_URL}/pressure/chamber/datastream`
    );

    //engine thermocouple data stream
    const engineTcSse = new EventSource(
      `${BASE_URL}/thermocouple/engine/datastream`
    );

    //stream receiving messages 
    supplyPressureSse.onmessage = (event) => {
      supplyPt = event.data.toString();
    };

    //when the stream is opened, display connected 
    supplyPressureSse.onopen = () => {
      supplySseStatus = "Connected";
    };

    //when the stream is error-ing out, display error
    supplyPressureSse.onerror = (_err) => {
      supplySseStatus = "Error";
    };

    enginePressureSse.onmessage = (event) => {
      enginePt = event.data.toString();
    };

    enginePressureSse.onopen = () => {
      engineSseStatus = "Connected";
    };

    enginePressureSse.onerror = (_err) => {
      engineSseStatus = "Error";
    };

    tankPressureSse.onmessage = (event) => {
      tankPt = event.data.toString();
    };

    tankPressureSse.onopen = () => {
      tankSseStatus = "Connected";
    };

    tankPressureSse.onerror = (_err) => {
      tankSseStatus = "Error";
    };

    chamberPressureSse.onmessage = (event) => {
      chamberPt = event.data.toString();
    };

    chamberPressureSse.onopen = () => {
      chamberSseStatus = "Connected";
    };

    chamberPressureSse.onerror = (_err) => {
      chamberSseStatus = "Error";
    };

    engineTcSse.onmessage = (event) => {
      engineTc = event.data.toString();
    };

    engineTcSse.onopen = () => {
      engineTcSseStatus = "Connected";
    };

    engineTcSse.onerror = (_err) => {
      engineTcSseStatus = "Error";
    };

    // Return a cleanup function that will be called when the component is unmounted
  });

//helper function map a string value to the Tvalvestate
  const mapToValveState = (value: string): TValveState => {
    switch (value) {
      case 'open':
        return 'Open';
      case 'closed':
        return 'Close';
      default:
        return 'Unknown';
    }
  };

//send GET requests to the server to actuate the respective sensors
// and update their states based on the response.
  const actuateEngineSensor = async () => {
    if (!selectedEngineOption || selectedEngineOption === "") return;

    await fetch(`${BASE_URL}/valve/engine?state=${selectedEngineOption}`, {
      method: "GET",
    }).then((response) => {
      if (response.ok) {
        engineState = mapToValveState(selectedEngineOption);
      } else {
        engineState = "Error";
      }
    });
  };

  const actuateSupplySensor = async () => {
    if (!selectedSupplyOption || selectedSupplyOption === "") return;

    await fetch(`${BASE_URL}/valve/relief?state=${selectedSupplyOption}`, {
      method: "GET",
    }).then((response) => {
      if (response.ok) {
        supplyState = mapToValveState(selectedSupplyOption);
      } else {
        supplyState = "Error";
      }
    });
  };

const startLogging = async () => {
  isLogging = true;
  await fetch(`${BASE_URL}/log_data/start`, {
    method: "GET",
  }).then((response) => {
    if (!response.ok) {
      console.error("Failed to start logging");
      isLogging = false;
    }
  });
};

const stopLogging = async () => {
  isLogging = false;
  // If your backend requires a call to stop logging, include it here
  await fetch(`${BASE_URL}/log_data/stop`, {
    method: "GET",
  }).then((response) => {
    if (!response.ok) {
      console.error("Failed to stop logging");
      // Optionally handle failure to stop logging
    }
  });
};

</script>

<!-- ... (rest of the code) -->


<div class="w-full min-h-screen flex flex-col container mx-auto p-4 justify-evenly max-w-screen-lg">
  <Heading
    tag="h1"
    class="font-bold"
    customSize="text-center text-4xl lg:text-5xl"
  >
    MHPR Nitrous Fill Box Control
  </Heading>

  <div class="flex justify-evenly gap-4">
    <Badge color={colorMap[engineSseStatus]} rounded class="px-2.5 py-0.5"
      >Tank bottom Pressure SSE: {engineSseStatus}</Badge
    >
    <Badge color={colorMap[supplySseStatus]} rounded class="px-2.5 py-0.5"
      >Supply Pressure SSE: {supplySseStatus}</Badge
    >
    <Badge color={colorMap[tankSseStatus]} rounded class="px-2.5 py-0.5"
      >Tank top Pressure SSE: {tankSseStatus}</Badge
    >
    <Badge color={colorMap[chamberSseStatus]} rounded class="px-2.5 py-0.5"
      >Chamber Pressure SSE: {chamberSseStatus}</Badge
    >
  </div>

  <!-- Bottom Row -->
  <div class="grid grid-cols-3 gap-4">
    <div class="flex flex-col gap-8">
      <div class="flex gap-2 lg:gap-4">
        <P class="text-lg lg:text-xl">Fill Valve</P>

        <span>
          <Badge color={colorMap[engineState]} rounded class="px-2.5 py-0.5">
            <Indicator size="sm" color={colorMap[engineState]} class="me-1.5" />
            <span>{engineState}</span>
          </Badge>
        </span>
      </div>

      <div class="flex gap-4">
        <Select items={actions} bind:value={selectedEngineOption} />
        <Button on:click={actuateEngineSensor}>Execute</Button>
      </div>
    </div>

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Tank Bottom Pressure</P>

      {#key enginePt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {enginePt} Bar
        </P>
      {/key}
    </div>

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Tank Top Pressure</P>

      {#key tankPt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {tankPt} Bar
        </P>
      {/key}
    </div>
  </div>

  <!-- Top Row -->
  <div class="grid grid-cols-3 gap-4">
    <div class="flex flex-col gap-8">
      <div class="flex gap-2 lg:gap-4">
        <P class="text-lg lg:text-xl">Dump Valve</P>

        <span>
          <Badge color={colorMap[supplyState]} rounded class="px-2.5 py-0.5">
            <Indicator size="sm" color={colorMap[supplyState]} class="me-1.5" />
            <span>{supplyState}</span>
          </Badge>
        </span>
      </div>

      <div class="flex gap-4">
        <Select items={actions} bind:value={selectedSupplyOption} />
        <Button on:click={actuateSupplySensor}>Execute</Button>
      </div>
    </div>

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Supply Pressure</P>

      {#key supplyPt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {supplyPt} Bar
        </P>
      {/key}
    </div>

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Chamber Pressure</P>

      {#key chamberPt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {chamberPt} Bar
        </P>
      {/key}
    </div>
  </div>

  <!-- Added buttons and logging light indicator -->
  <div class="flex gap-4 mt-4 items-center">
    <Button on:click={startLogging}>Start Logging</Button>
    <Button on:click={stopLogging}>Stop Logging</Button>
    <Indicator size="sm" color={isLogging ? "green" : "red"} class="me-1.5" />

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Engine Temp</P>
      {#key engineTc}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {engineTc} °C
        </P>
      {/key}
    </div>
  </div>
</div>
