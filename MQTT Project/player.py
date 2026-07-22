import random

from config import GRID_WIDTH, GRID_HEIGHT

colors = [
    (231, 76, 60),
    (52, 152, 219),
    (46, 204, 113),
    (241, 196, 15),
    (155, 89, 182),
    (26, 188, 156),
    (230, 126, 34),
    (149, 165, 166),
]


class Player:
    def __init__(self, player_id, name=None):
        self.id = player_id
        self.name = name or player_id
        self.x = random.randint(0, GRID_WIDTH - 1)
        self.y = random.randint(0, GRID_HEIGHT - 1)
        self.color = random.choice(colors)

    def move(self, dx, dy):
        new_x = max (0, min(GRID_WIDTH - 1, self.x + dx))
        new_y = max(0, min(GRID_HEIGHT - 1, self.y + dy))
        moved = (new_x, new_y) != (self.x, self.y)
        self.x, self.y = new_x, new_y
        return moved