from position import Position
from bfsPath import Pathfinder

class Player:
    def __init__(self, position, color):
        self.position = position
        self.home_position = position
        self.team = None
        self.Board = None
        self.color = color
        self.canvas_item = None
        self.proposed_move = None

    def reset(self):
        self.position = self.home_position
    
    def run(self):
        carrier = self.board.possession_player

        if self is carrier:
            target = Position(self.team.attack_goal_col, self.position.row)
        else:
            target = carrier.position

        obstacles = self.board.occupied_spots()
        self.proposed_move = Pathfinder.next_step(
            self.position, target, self.board.cols, self.board.rows, obstacles
        )
        
