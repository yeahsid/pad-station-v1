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
    | "primary";

  const BASE_URL = "http://padstation-prod.local:8000";

  const colorMap: Record<TConnectionStatus | TValveState, TColorType> = {
    Connected: "green",
    Error: "red",
    Unknown: "dark",
    Open: "green",
    Close: "red",
  };

  let supplyPt: string;
  let fillPt: string;
  let tankPt: string;
  let testStandLoad: string;
  let tankTc: string;
  let fillState: TValveState = "Unknown";
  let supplyState: TValveState = "Unknown";
  let pilotState: TValveState = "Unknown";
  let selectedFillOption: string | "Unknown";
  let selectedSupplyOption: string | "Unknown";
  let selectedPilotOption: string | "Unknown";
  let fillSseStatus: TConnectionStatus = "Unknown";
  let supplySseStatus: TConnectionStatus = "Unknown";
  let tankSseStatus: TConnectionStatus = "Unknown";
  let tankTcSseStatus: TConnectionStatus = "Unknown";

  let isLogging = false;

  onMount(() => {
    const fillPressureSse = new EventSource(
      `${BASE_URL}/pressure/fill/datastream`,
    );

    const supplyPressureSse = new EventSource(
      `${BASE_URL}/pressure/supply/datastream`,
    );

    const tankPressureSse = new EventSource(
      `${BASE_URL}/pressure/tank_top/datastream`,
    );

    const tankTcSse = new EventSource(
      `${BASE_URL}/thermocouple/tank_thermocouple/datastream`,
    );

    const testStandLoadCell = new EventSource(
      `${BASE_URL}/load_cell/test_stand/datastream`,
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

    fillPressureSse.onmessage = (event) => {
      fillPt = event.data.toString();
    };

    fillPressureSse.onopen = () => {
      fillSseStatus = "Connected";
    };

    fillPressureSse.onerror = (_err) => {
      fillSseStatus = "Error";
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

    tankTcSse.onmessage = (event) => {
      tankTc = event.data.toString();
    };

    tankTcSse.onopen = () => {
      tankTcSseStatus = "Connected";
    };

    tankTcSse.onerror = (_err) => {
      tankTcSseStatus = "Error";
    };

    testStandLoadCell.onmessage = (event) => {
      testStandLoad = event.data.toString();
    };

    return () => {
      fillPressureSse.close();
      supplyPressureSse.close();
      tankPressureSse.close();
      tankTcSse.close();
      testStandLoadCell.close();
    };
  });

  const mapToValveState = (value: string): TValveState => {
    switch (value) {
      case "open":
        return "Open";
      case "closed":
        return "Close";
      default:
        return "Unknown";
    }
  };

  const actuateFillValve = async () => {
    if (!selectedFillOption || selectedFillOption === "") return;

    await fetch(`${BASE_URL}/valve/engine?state=${selectedFillOption}`, {
      method: "GET",
    }).then((response) => {
      if (response.ok) {
        fillState = mapToValveState(selectedFillOption);
      } else {
        fillState = "Error";
      }
    });
  };

  const actuateSupplyValve = async () => {
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

  const actuatePilotValve = async () => {
    if (!selectedPilotOption || selectedPilotOption === "") return;

    await fetch(
      `${BASE_URL}/pilot_valve/pilot_valve?state=${selectedPilotOption}&timeout=5`,
      {
        method: "GET",
      },
    ).then((response) => {
      if (response.ok) {
        pilotState = mapToValveState(selectedPilotOption);
      } else {
        pilotState = "Error";
      }
    });
  };

  const startLogging = async () => {
    isLogging = true;
    try {
      const response = await fetch(`${BASE_URL}/log_data/start`, {
        method: "GET",
      });
      if (!response.ok) {
        console.error("Failed to start logging");
        isLogging = false;
      }
    } catch (error) {
      console.error("Error occurred while starting logging:", error);
      isLogging = false;
    }
  };

  const stopLogging = async () => {
    isLogging = false;
    try {
      const response = await fetch(`${BASE_URL}/log_data/stop`, {
        method: "GET",
      });
      if (!response.ok) {
        console.error("Failed to stop logging");
      }
    } catch (error) {
      console.error("Error occurred while stopping logging:", error);
    }
  };

  const ignite = async () => {
    try {
      const response = await fetch(`${BASE_URL}/ignition?delay=1`, {
        method: "GET",
      });
      if (!response.ok) {
        console.error("Failed to ignite");
      }
    } catch (error) {
      console.error("Error occurred while igniting:", error);
    }
  };

  const fire_qd = async () => {
    try {
      const response = await fetch(`${BASE_URL}/relays/qd`, {
        method: "GET",
      });
      if (!response.ok) {
        console.error("Failed to fire QD");
      }
    } catch (error) {
      console.error("Error occurred while firing QD:", error);
    }
  };

  const fire_vent = async () => {
    try {
      const response = await fetch(`${BASE_URL}/relays/vent`, {
        method: "GET",
      });
      if (!response.ok) {
        console.error("Failed to fire Vent");
      }
    } catch (error) {
      console.error("Error occurred while firing Vent");
    }
  };
</script>

<!-- ... (rest of the code) -->

<div
  class="w-full min-h-screen flex flex-col container mx-auto p-4 justify-evenly max-w-screen-lg"
>
  <Heading
    tag="h1"
    class="font-bold"
    customSize="text-center text-4xl lg:text-5xl"
  >
    MHPR Nitrous Fill Box Control
  </Heading>

  <div class="flex justify-evenly gap-4">
    <Badge color={colorMap[fillSseStatus]} rounded class="px-2.5 py-0.5"
      >Fill Pressure SSE: {fillSseStatus}</Badge
    >
    <Badge color={colorMap[supplySseStatus]} rounded class="px-2.5 py-0.5"
      >Supply Pressure SSE: {supplySseStatus}</Badge
    >
    <Badge color={colorMap[tankSseStatus]} rounded class="px-2.5 py-0.5"
      >Tank Pressure SSE: {tankSseStatus}</Badge
    >
  </div>

  <!-- Pilot Valve -->
  <div class="grid grid-cols-3 gap-4">
    <div class="flex flex-col gap-8">
      <div class="flex gap-2 lg:gap-4">
        <P class="text-lg lg:text-xl">Pilot Valve</P>

        <span>
          <Badge color={colorMap[pilotState]} rounded class="px-2.5 py-0.5">
            <Indicator size="sm" color={colorMap[pilotState]} class="me-1.5" />
            <span>{pilotState}</span>
          </Badge>
        </span>
      </div>

      <div class="flex gap-4">
        <Select items={actions} bind:value={selectedPilotOption} />
        <Button on:click={actuatePilotValve}>Execute</Button>
      </div>
    </div>
  </div>

  <!-- Bottom Row -->
  <div class="grid grid-cols-3 gap-4">
    <div class="flex flex-col gap-8">
      <div class="flex gap-2 lg:gap-4">
        <P class="text-lg lg:text-xl">Fill Valve</P>

        <span>
          <Badge color={colorMap[fillState]} rounded class="px-2.5 py-0.5">
            <Indicator size="sm" color={colorMap[fillState]} class="me-1.5" />
            <span>{fillState}</span>
          </Badge>
        </span>
      </div>

      <div class="flex gap-4">
        <Select items={actions} bind:value={selectedFillOption} />
        <Button on:click={actuateFillValve}>Execute</Button>
      </div>
    </div>

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Fill Pressure</P>

      {#key fillPt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {fillPt} Bar
        </P>
      {/key}
    </div>

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Tank Pressure</P>

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
        <Button on:click={actuateSupplyValve}>Execute</Button>
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
      <P class="text-lg lg:text-xl text-end">Test Stand Force</P>
      {#key testStandLoad}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {testStandLoad} N
        </P>
      {/key}
    </div>
  </div>

  <!-- Added buttons and logging light indicator -->

  <div class="grid grid-cols-3 gap-4">
    <div class="flex flex-col gap-8">
      <div class="flex gap-4">
        <Button on:click={startLogging}>Start Logging</Button>
        <Button on:click={stopLogging}>Stop Logging</Button>
        <Indicator
          size="sm"
          color={isLogging ? "green" : "red"}
          class="me-1.5"
        />
      </div>
    </div>

    <div class="flex flex-col gap-4">
      <P class="text-lg lg:text-xl text-end">Tank Temp</P>
      {#key tankTc}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {tankTc} °C
        </P>
      {/key}
    </div>
  </div>

  <div class="flex flex-col gap-8">
    <div class="flex gap-4">
      <Button
        class="bg-red-500 text-white text-xl py-4 px-8 rounded"
        on:click={ignite}>Ignite</Button
      >
      <Button on:click={fire_qd}>Fire QD</Button>
      <Button on:click={fire_vent}>Fire Vent</Button>
    </div>
  </div>
</div>
