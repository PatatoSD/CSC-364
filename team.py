class Team:
    def __init__(self, name, color, attack_goal_col):
        self.name = name
        self.color = color
        self.attack_goal_col = attack_goal_col
        self.players = []
        self.score = 0
    
    def add_player(self, player):
        self.players.append(player)
        player.team = self