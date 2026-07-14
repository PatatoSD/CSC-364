from tkinter import *
import player

#Board Creation
root = Tk()
root.title("Ball Chase Game")
root.geometry("1200x700")
root.grid_columnconfigure(0, weight=1)

canvas_width = 950
canvas_height = 425


lbl = Label(root, text = "Welcome to the Ball Chase Game!")
lbl.grid(row=0, column=0, pady=10)

#checks if the button was clicked
def clicked():
    lbl.configure(text="Button Clicked!")
    player.game_loop(board, root)

btn = Button(root, text="Start Game", command=clicked)
btn.grid(row=1, column=0, pady=10)

scorelbl = Label(root, text = "Home: %d | Away: %d" % (player.redScore, player.blueScore))
scorelbl.grid(row=2, column=0, pady=10)

turnlbl = Label(root, text = "Turn: %d" %(player.turnCount))
turnlbl.grid(row=3, column=0, pady = 10)


board = Canvas(root, width = canvas_width, height = canvas_height, bg = "white")
board.grid(row = 4, column = 0, pady = 10)
player.draw_grid(board, canvas_width, canvas_height, player.cell_size)

rect_width = player.cell_size
rect_height = player.cell_size * 5
top_y = (canvas_height - rect_height) / 2
bottom_y = top_y + rect_height

board.create_rectangle(0, 0, rect_width, canvas_height + player.cell_size, fill = "#f0f0f0" )
board.create_rectangle(canvas_width - rect_width, 0, canvas_width + 100, canvas_height + player.cell_size, fill="#f0f0f0")

board.create_rectangle(2, top_y, rect_width, bottom_y, fil="gold")
board.create_rectangle(canvas_width - rect_width, top_y, canvas_width, bottom_y, fill="gold")

player.player_setup(board)

def update_labels():
    scorelbl.configure(text= "Home: %d | Away: %d" % (player.redScore, player.blueScore))
    turnlbl.configure(text="Turn: %d " % player.turnCount)
    root.after(200, update_labels)

update_labels()
root.mainloop() 