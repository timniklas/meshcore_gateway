import asyncio
from meshcore import MeshCore
from meshcore_client import MeshcoreClient
from meshtastic_client import MeshtasticClient
from bridge import Bridge
from config import (
    MESHCORE_SERIAL_INTERFACE,
    MESHCORE_BAUDRATE,
    MESHTASTIC_HOST,
)

async def main():
    loop = asyncio.get_running_loop()

    # Meshcore
    meshcore_interface = await MeshCore.create_serial(MESHCORE_SERIAL_INTERFACE)
    meshcore_client = MeshcoreClient(
        interface=meshcore_interface,
        on_incoming_text=lambda s, m: asyncio.sleep(0),
    )

    # Meshtastic (TCP)
    meshtastic_client = MeshtasticClient(
        host=MESHTASTIC_HOST,
        loop=loop,
        on_incoming_text=lambda s, m: asyncio.sleep(0),
    )

    # Bridge verbinden
    bridge = Bridge(meshcore_client, meshtastic_client)
    meshcore_client.on_incoming_text = bridge.from_meshcore
    meshtastic_client.on_incoming_text = bridge.from_meshtastic

    # Verbindungen aufbauen
    await meshcore_client.connect()
    meshtastic_client.connect()

    print("[main] MeshBridge running...")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
