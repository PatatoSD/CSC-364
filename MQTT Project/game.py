import uuid
import pygame

from blackboard import Blackboard
from config import CELL_SIZE, GRID_HEIGHT, GRID_WIDTH
from mqttConn import MQTTConnection
from player import Player

backGround = (30, 30, 30)
gridColor = (60, 60, 60)
TextColor = (230, 230, 230)

def main():
    name = input("Enter your player name: ").strip() or "player"
    player_id = f"{name}-{uuid.uuid4().hex[:6]}"

    player = Player(player_id, name=name)
    blackboard = Blackboard()

    def player_message(data):
        if data["player_id"] == player_id:
            return
        blackboard.update_player(
            data["player_id"],
            data["x"],
            data["y"],
            tuple(data["color"]),
            data.get("name", data["player_id"]),
        )

    def player_leave(pid):
        if pid != player_id:
            blackboard.remove_player(pid)

    mqtt_con = MQTTConnection(player_id, player_message, player_leave)
    mqtt_con.connect()
    mqtt_con.publish_position(player.x, player.y, player.color, player.name)

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption(f"Project 3 Grid Game - {name}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    running = True
    try:
        while running:
            moved = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    dx = dy = 0
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        dx = -1
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        dx = 1
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        dy = -1
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        dy = 1
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    if dx or dy:
                        moved = player.move(dx, dy)
            if moved:
                mqtt_con.publish_position(player.x, player.y, player.color, player.name)

            screen.fill(backGround)
            _draw_grid(screen)
            _draw_players(screen, blackboard.snapshot(), font)
            _draw_token(screen, player.x, player.y, player.color, f"{player.name} (you)", font)
            pygame.display.flip()
            clock.tick(30)
    finally:
        mqtt_con.disconnect()
        pygame.quit()

def _draw_grid(screen):
    for gx in range(GRID_WIDTH + 1):
        x = gx * CELL_SIZE
        pygame.draw.line(screen, gridColor, (x, 0), (x, GRID_HEIGHT * CELL_SIZE))
    for gy in range(GRID_HEIGHT + 1):
        y = gy * CELL_SIZE
        pygame.draw.line(screen, gridColor, (0, y), (GRID_WIDTH * CELL_SIZE, y))

def _draw_players(screen, players, font):
    for p in players.values():
        _draw_token(screen, p["x"], p["y"], p["color"], p["name"], font)

def _draw_token(screen, x, y, color, label, font):
    cx = x * CELL_SIZE + CELL_SIZE // 2
    cy = y * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, color, (cx, cy), CELL_SIZE // 2 - 4)
    text = font.render(label, True, TextColor)
    screen.blit(text, (cx - text.get_width() // 2, cy - 14))

if __name__ == "__main__":
    main()