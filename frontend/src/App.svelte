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

  type TConnectionStatus = "Connected" | "Error" | "Unknown";
  type TValveState = "Open" | "Close" | "Error" | "Unknown";
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

  const BASE_URL = "http://padstation.local:8000";

  const colorMap: Record<TConnectionStatus | TValveState, TColorType> = {
    Connected: "green",
    Error: "red",
    Unknown: "dark",
    Open: "green",
    Close: "red",
  };

  let supplyPt: string;
  let enginePt: string;
  let engineState: TValveState = "Unknown";
  let supplyState: TValveState = "Unknown";
  let selectedEngineOption: string | undefined;
  let selectedSupplyOption: string | undefined;
  let engineSseStatus: TConnectionStatus = "Unknown";
  let supplySseStatus: TConnectionStatus = "Unknown";

  onMount(() => {
    const enginePressureSse = new EventSource(
      `${BASE_URL}/pressure/engine/datastream`
    );

    const supplyPressureSse = new EventSource(
      `${BASE_URL}/pressure/supply/datastream`
    );

    supplyPressureSse.onmessage = (event) => {
      supplyPt = event.data.toString();
    };

    supplyPressureSse.onopen = () => {
      supplySseStatus = "Connected";
    };

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

<!-- ... (rest of the code) -->

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
