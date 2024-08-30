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

  /*gyu
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
    | "primary";
  //base url is for API calls to get the data from the backend
  const BASE_URL = "http://padstation-prod.local:8000";

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
  let tankTc: string;
  let testStandLoad: string;
  let engineState: TValveState = "Unknown";
  let supplyState: TValveState = "Unknown";
  let pilotState: TValveState = "Unknown";
  let selectedEngineOption: string | "Unknown";
  let selectedSupplyOption: string | "Unknown";
  let selectedPilotOption: string | "Unknown";
  let engineSseStatus: TConnectionStatus = "Unknown";
  let supplySseStatus: TConnectionStatus = "Unknown";
  let tankSseStatus: TConnectionStatus = "Unknown";
  let chamberSseStatus: TConnectionStatus = "Unknown";
  let tankTcSseStatus: TConnectionStatus = "Unknown";

  // New state variable for logging status
  let isLogging = false;

  //The onMount function sets up EventSource connections to receive real-time updates
  onMount(() => {
    //pressure data stream
    const enginePressureSse = new EventSource(
      ``,
    );

    //pressure data stream
    const supplyPressureSse = new EventSource(
      `${BASE_URL}/pressure/supply/datastream`,
    );

    //pressure data stream
    const tankPressureSse = new EventSource(
      `${BASE_URL}/pressure/tank_top/datastream`,
    );

    //pressure data stream
    const chamberPressureSse = new EventSource(
      `${BASE_URL}/pressure/chamber/datastream`,
    );

    //engine thermocouple data stream
    const tankTcSse = new EventSource(
      `${BASE_URL}/thermocouple/tank_thermocouple/datastream`,
    );

    const testStandLoadCell = new EventSource(
      `${BASE_URL}/load_cell/test_stand/datastream`,
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
      // Update the state or UI with only the latest data
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

    // Return a cleanup function that will be called when the component is unmounted
    return () => {
      enginePressureSse.close();
      supplyPressureSse.close();
      tankPressureSse.close();
      chamberPressureSse.close();
      tankTcSse.close();
      testStandLoadCell.close();
    };
  });

  //helper function map a string value to the Tvalvestate
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

  const actuatePilotValve = async () => {
    if (!selectedPilotOption || selectedPilotOption === "") return;

    await fetch(
      `${BASE_URL}/pilot_valve/pilot_valve?state=${selectedPilotOption}&timeout=50`,
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
        // Optionally handle failure to start logging
      }
    } catch (error) {
      console.error("Error occurred while starting logging:", error);
      isLogging = false;
      // Optionally handle the error
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
        // Optionally handle failure to stop logging
      }
    } catch (error) {
      console.error("Error occurred while stopping logging:", error);
      // Optionally handle the error
    }
  };

  const ignite = async () => {
    try {
      const response = await fetch(
        `${BASE_URL}/ignition?delay=1`,
        {
          method: "GET",
        },
      );
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
      console.error("Error occurred while firing Vent:", error);
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
    <Badge color={colorMap[engineSseStatus]} rounded class="px-2.5 py-0.5"
      >Chamber SSE: {engineSseStatus}</Badge
    >
    <Badge color={colorMap[supplySseStatus]} rounded class="px-2.5 py-0.5"
      >Supply Pressure SSE: {supplySseStatus}</Badge
    >
    <Badge color={colorMap[tankSseStatus]} rounded class="px-2.5 py-0.5"
      >Tank top Pressure SSE: {tankSseStatus}</Badge
    >
    <Badge color={colorMap[chamberSseStatus]} rounded class="px-2.5 py-0.5"
      >Fill Pressure SSE: {chamberSseStatus}</Badge
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
      <P class="text-lg lg:text-xl text-end">Chamber</P>

      {#key enginePt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {enginePt} Bar
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
      <P class="text-lg lg:text-xl text-end">Fill Pressure</P>

      {#key chamberPt}
        <P class="font-bold text-2xl lg:text-4xl text-end">
          {chamberPt} Bar
        </P>
      {/key}
    </div>
  </div>

  <div class="grid grid-cols-3 gap-4">
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
      <Button on:click={ignite}>Ignite</Button>
      <Button on:click={fire_qd}>Fire QD</Button>
      <Button on:click={fire_vent}>Fire Vent</Button>
    </div>
  </div>
</div>
