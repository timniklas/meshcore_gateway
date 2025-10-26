import asyncio
from pubsub import pub
import meshtastic.tcp_interface

class MeshtasticClient:
    """
    TCP-Verbindung zu Meshtasticd (z. B. localhost:4403)
    """

    def __init__(self, host, loop, on_incoming_text):
        self._host = host
        self.loop = loop
        self.on_incoming_text = on_incoming_text
        self.interface = None

    def connect(self):
        # TCP-Verbindung aufbauen
        self.interface = meshtastic.tcp_interface.TCPInterface(self._host)
        pub.subscribe(self._handle_message_threaded_cb, "meshtastic.receive.text")
        print(f"[meshtastic] Connected via TCP to {self._host}")

    def send_message(self, message: str):
        if not self.interface:
            raise RuntimeError("Meshtastic not connected")
        self.interface.sendText(message, wantAck=True)
        print(f"[meshtastic] Sent: {message}")

    def _get_node_name(self, node_id):
        """Versucht, den Knotennamen anhand der Node-ID zu ermitteln"""
        if not self.interface or not hasattr(self.interface, "nodes"):
            return str(node_id)

        for node in self.interface.nodes.values():
            if node.get("num") == node_id:
                user = node.get("user", {})
                return user.get("longName") or user.get("shortName") or str(node_id)
        return str(node_id)

    def _handle_message_threaded_cb(self, packet, interface):
        try:
            if packet.get("toId") != "^all":
                return

            nodenum = packet.get("from")
            decoded = packet.get("decoded") or {}
            message = decoded.get("text", "")
            sender_name = self._get_node_name(nodenum)

            print(f"[meshtastic] recv from {sender_name}: {message}")

            fut = asyncio.run_coroutine_threadsafe(
                self.on_incoming_text(f"Meshtastic {sender_name}:{message}"),
                self.loop,
            )
            fut.add_done_callback(lambda f: f.exception() and print("meshtastic cb error:", f.exception()))
        except Exception as e:
            print("meshtastic cb error:", e)
