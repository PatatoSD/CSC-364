import time
import threading

class Blackboard:
    def __init__(self, stale_after=15.0):
        self._lock = threading.Lock()
        self._players = {}
        self._stale_after = stale_after

    def update_player(self, player_id, x, y, color, name):
        with self._lock:
            self._players[player_id] = {
                "x": x,
                "y": y,
                "color": color,
                "name": name,
                "last_seen": time.time()
            }

    def remove_player(self, player_id):
        with self._lock:
            self._players.pop(player_id, None)

    def snapshot(self):
        now = time.time()
        with self._lock:
            stale_ids = [
                pid for pid, p in self._players.items()
                if now - p["last_seen"] > self._stale_after
            ]
            for pid in stale_ids:
                del self._players[pid]
            return dict(self._players)