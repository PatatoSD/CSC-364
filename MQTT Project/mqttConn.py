import json
import paho.mqtt.client as mqtt

from config import BROKER_HOST, BROKER_PORT, TOPIC

class MQTTConnection:
    def __init__(self, player_id, player_message, player_leave):
        self.player_id = player_id
        self.player_message = player_message
        self.player_leave, player_leave

        self.positions_wild = f"{TOPIC}/players/+"
        self.my_topic = f"{TOPIC}/players/{player_id}"

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=player_id,
            clean_session=True,
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        leave_payload = json.dumps({"type": "leave", "player_id": player_id})
        self.client.will_set(self.my_topic, payload=leave_payload, qos=1, retain=True)

        def connect(self):
            self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=30)
            self.client.loop_start()

        def disconnect(self):
            leave_payload=json.dumps({"type": "leave", "player_id": self.player_id})
            self.client.publish(self.my_topic, leave_payload, qos=1, retain=True)
            self.client.loop_stop()
            self.client.disconnect()

        def publish_position(self, x, y, color, name):
            payload = json.dumps({
                "type": "move",
                "player_id": self.player_id,
                "x": x,
                "y": y,
                "color": list(color),
                "name": name,
            })
            self.client.publish(self.my_topic, payload, qos=0, retain=True)

        def _on_connect(self, client, userdata, flags, reason_code, props):
            client.subscribe(self.positions_wild)

        def _on_message(self, client, userdata, msg):
            if not msg.payload:
                return
            try:
                data = json.loads(msg.payload.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return

            if data.get("type") == "leave":
                self.player_leave(data.get("player_id"))
            elif data.get("type") == "move":
                self.player_message(data)