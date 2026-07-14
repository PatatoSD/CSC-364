from tkinter import *
from position import Position
from team import Team
from player import Player
from GameBoard import GameBoard

cell_size = 25
canvas_width = 950
canvas_height = 425
cols = canvas_width // cell_size
rows = canvas_height // cell_size

root = Tk()
root.title("Ball Chase Game")
root.geometry("1200x700")
root.grid_columnconfigure(0, weight=1)

lbl = Label(root, text="Welcome to the Ball Chase Game!")
lbl.grid(row=0, column=0, pady=10)


def grid_to_pixels(pos):
    x1, y1 = pos.col * cell_size, pos.row * cell_size
    return x1, y1, x1 + cell_size, y1 + cell_size

def draw_grid(canvas, width, height, size, color="lightgray"):
    for x in range(0, width, size):
        canvas.create_line(x, 0, x, height, fill=color)
    for y in range(0, height, size):
        canvas.create_line(0, y, width, y, fill=color)


redTeam = Team("A", "red", attack_goal_col = cols - 1)
blueTeam = Team("B", "blue", attack_goal_col=0)

red_rows = [2, 5, 8, 11, 14]
blue_rows = [2, 5, 8, 11, 14]
for r in red_rows:
    redTeam.add_player(Player(Position(cols//2 - 4, r), "red"))
for r in blue_rows:
    blueTeam.add_player(Player(Position(cols//2 + 4, r), "blue"))

board_state = GameBoard(cols, rows, redTeam, blueTeam)
board_state.possession_player = redTeam.players[2]

def clicked():
    lbl.configure(text="Game Start!")
    tick()

btn = Button(root, text="Start Game", command=clicked)
btn.grid(row=1, column=0, pady=10)

scorelbl = Label(root, text="Home: 0 | Away: 0")
scorelbl.grid(row=2, column=0, pady=10)

turnlbl = Label(root, text="Turn: 0")
turnlbl.grid(row=3, column=0, pady=10)

board = Canvas(root, width=canvas_width, height=canvas_height, bg="white")
board.grid(row=4, column=0, pady=10)
draw_grid(board, canvas_width, canvas_height, cell_size)

board.create_rectangle(2, 0, cell_size, canvas_height, fil="gold")
board.create_rectangle(canvas_width - cell_size, 0, canvas_width, canvas_height, fill="gold")

for p in board_state.all_players:
    x1, y1, x2, y2 = grid_to_pixels(p.position)
    p.canvas_item = board.create_rectangle(x1, y1, x2, y2, fill=p.color)

ball_item = board.create_oval(0, 0, 1, 1, fill="orange")    

def redraw():
    for p in board_state.all_players:
        x1, y1, x2, y2 = grid_to_pixels(p.position)
        board.coords(p.canvas_item, x1, y1, x2, y2)
    carrier =board_state.possession_player
    cx1, cy1, cx2, cy2 = grid_to_pixels(carrier.position)
    board.coords(ball_item, cx1 + 5, cy1 + 5, cx1 + 15, cy1 + 15)
    scorelbl.configure(text=f"Home: {redTeam.score} | Away: {blueTeam.score}")
    turnlbl.configure(text=f"Turn: {board_state.turn_count}")

def tick():
    board_state.run_turn()
    redraw()
    root.after(200, tick)

root.mainloop()