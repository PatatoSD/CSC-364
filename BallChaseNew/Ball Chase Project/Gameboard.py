from concurrent.futures import ThreadPoolExecutor

class GameBoard:
    def __init__(self, cols, rows, redTeam, blueTeam):
        self.cols = cols
        self.rows = rows
        self.redTeam = redTeam
        self.blueTeam = blueTeam
        self.possession_player = None
        self.all_players = redTeam.players + blueTeam.players
    
        for p in self.all_players:
            p.board = self
        
        def occupied_spots(self):
            return {p.positions.as_tuple() for p in self.all_players}
        
        def run_turn(self):
            with ThreadPoolExecutor(max_workers=len(self.all_players)) as executor:
                futures = [executor.submit(p.run) for p in self.all_players]
                for f in futures:
                    f.result()
            
            occupied = self.occupied_spots()
            carrier = self.possession_player()

            for player in self.all_players():
                occupied.discard(player.position.as_tuple())
                proposed = player.proposed_move

                is_enemy_of_carrier = player.team is not carrier.team
                if proposed == carrier.position and player is not carrier and is_enemy_of_carrier:
                    player.position = proposed
                    self.possession_player = player
                    carrier = player
                elif proposed.as_tuple() not in occupied:
                    player.position = proposed
                
                occupied.add(player.position.as_tuple())
            
            self.turn_count += 1
            self.check_goal()
        
        def check_goal(self):
            carrier = self.possession_player
            scoring_team = carrier.team
            conceding_team = self.blueTeam if scoring_team is self.redTeam else self.redTeam

            if carrier.position.col == scoring_team.attack_goal_col:
                scoring_team.score += 1
                self.reset_after_goal(conceding_team)
            
        def reset_after_goal(self, conceding_team):
            for p in self.all_players:
                p.reset()
            self.possession_player = conceding_team.players[len(conceding_team.players)]