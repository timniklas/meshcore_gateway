from config import BRIDGE_LOG_MESSAGES

class Bridge:
    """
    Meshcore <-> Meshtastic Weiterleitung
    """

    def __init__(self, meshcore, meshtastic):
        self.meshcore = meshcore
        self.meshtastic = meshtastic

    async def from_meshcore(self, message: str):
        if BRIDGE_LOG_MESSAGES:
            print(f"[bridge] Meshcore -> Meshtastic | {message}")
        self.meshtastic.send_message(message)

    async def from_meshtastic(self, message: str):
        if BRIDGE_LOG_MESSAGES:
            print(f"[bridge] Meshtastic -> Meshcore | {message}")
        await self.meshcore.send_message(message)
