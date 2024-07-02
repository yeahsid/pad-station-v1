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
  const BASE_URL = "http://localhost:8000";

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
  let engineState: TValveState = "Unknown";
  let supplyState: TValveState = "Unknown";
  let selectedEngineOption: string | undefined;
  let selectedSupplyOption: string | undefined;
  let engineSseStatus: TConnectionStatus = "Unknown";
  let supplySseStatus: TConnectionStatus = "Unknown";

//The onMount function sets up EventSource connections to receive real-time updates
  onMount(() => {
    //pressure data stream
    const enginePressureSse = new EventSource(
      `${BASE_URL}/pressure/engine/datastream`
    );

    //pressure data stream
    const supplyPressureSse = new EventSource(
      `${BASE_URL}/pressure/supply/datastream`
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
</script>

/*HTML template to create user interface*/
<!-- ... (rest of the code) -->

/*
<div class="w-full min-h-screen flex flex-col container mx-auto p-4 justify-evenly max-w-screen-md">
  <Heading
    tag="h1"
    class="font-bold"
    customSize="text-center text-4xl lg:text-5xl"
  >
    MHPR Nitrous Fill Box Control
  </Heading>

  <div class="flex gap-4">
    <Badge color={colorMap[engineSseStatus]} rounded class="px-2.5 py-0.5"
      >Engine Pressure SSE: {engineSseStatus}</Badge
    >
    <Badge color={colorMap[supplySseStatus]} rounded class="px-2.5 py-0.5"
      >Supply Pressure SSE: {supplySseStatus}</Badge
    >
  </div>

  <!-- Bottom Row -->
  <div class="grid grid-cols-2 gap-4">
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

    <div class="flex flex-col gap-4 place-self-end">
      <P class="text-lg lg:text-xl text-end">Engine Pressure</P>

      {#key enginePt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {enginePt} Bar
        </P>
      {/key}
    </div>
  </div>

  <!-- Top Row -->
  <div class="grid grid-cols-2 gap-4">
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

    <div class="flex flex-col gap-4 place-self-end">
      <P class="text-lg lg:text-xl text-end">Supply Pressure</P>

      {#key supplyPt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {supplyPt} Bar
        </P>
      {/key}
    </div>
  </div>
</div>
*/


<div class="w-full min-h-screen flex flex-col container mx-auto p-4 justify-evenly max-w-screen-md">
  <Heading
    tag="h1"
    class="font-bold"
    customSize="text-center text-4xl lg:text-5xl"
  >
    MHPR Nitrous Fill Box Control
  </Heading>

  <div class="flex gap-4">
    <Badge color={colorMap[engineSseStatus]} rounded class="px-2.5 py-0.5">
      Engine Pressure SSE: {engineSseStatus}
    </Badge>
    <Badge color={colorMap[supplySseStatus]} rounded class="px-2.5 py-0.5">
      Supply Pressure SSE: {supplySseStatus}
    </Badge>
  </div>

  <div class="grid grid-cols-2 gap-4">
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

    <div class="flex flex-col gap-4 place-self-end">
      <P class="text-lg lg:text-xl text-end">Engine Pressure</P>

      {#key enginePt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {enginePt} Bar
        </P>
      {/key}
    </div>
  </div>

  <div class="grid grid-cols-2 gap-4">
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

    <div class="flex flex-col gap-4 place-self-end">
      <P class="text-lg lg:text-xl text-end">Supply Pressure</P>

      {#key supplyPt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {supplyPt} Bar
        </P>
      {/key}
    </div>
  </div>

  <div class="flex gap-4 mt-4">
    <Button>Start Logging</Button>
    <Button>PV Up</Button>
    <Button>PV Down</Button>
  </div>
</div>