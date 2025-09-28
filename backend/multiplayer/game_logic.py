import random
from collections import Counter
import multiplayer.room_manager as rm
class VotingSession:

    def __init__(self, room_code):
        self.room_code = room_code
        self.votes = {}
        self.num_responses = 0
        self.total_players = len(rm.get_players(room_code))
        self.voted_players = []

    def process_player_response(self, room, player_name, option_id):
        if room != self.room_code:
            raise ValueError("Room code does not match voting session")
        
        if player_name in self.voted_players:
            return None
        
        self.voted_players.append(player_name)
        self.num_responses += 1

        if option_id not in self.votes:
            self.votes[option_id] = 0
        self.votes[option_id] += 1

        if self.num_responses < self.total_players:
            return None

        # all players have voted, compute final option
        max_votes = -1
        final_option = random.choice(list(self.votes.keys()))
        for option, vote in self.votes.items():
            if vote > max_votes:
                max_votes = vote
                final_option = option

        return final_option
