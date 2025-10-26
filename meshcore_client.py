import asyncio
from meshcore import MeshCore, EventType

class MeshcoreClient:
    def __init__(self, interface, on_incoming_text):
        self.interface = interface
        self.on_incoming_text = on_incoming_text  # async (name, message) -> None
        self.connected = False
        self.interface.subscribe(EventType.DISCONNECTED, self._on_disconnected)
        self.interface.subscribe(EventType.CHANNEL_MSG_RECV, self._handle_message)

    async def connect(self):
        if self.connected:
            raise RuntimeError("meshcore already connected")
        self.connected = True
        await self.interface.start_auto_message_fetching()

    async def send_message(self, message: str):
        if not self.connected:
            raise RuntimeError("meshcore not connected")
        result = await self.interface.commands.send_chan_msg(0, message)
        if result.type == EventType.ERROR:
            raise RuntimeError("meshcore message send failed")

    async def _on_disconnected(self, event):
        self.connected = False
        raise RuntimeError("meshcore disconnected")

    async def _handle_message(self, event):
        message = event.payload['text']
        print("[meshcore]", f"{message}")
        await self.on_incoming_text(message)