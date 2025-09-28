import random
from collections import Counter
import multiplayer.room_manager as rm

class VotingSession :

    def __init__(self, room_code):
        self.room_code = room_code
        self.votes = {}
        self.num_responses = 0
        self.total_players = len(rm.get_players(room_code))
        self.voted_players = []


    def process_player_response(self, room, player_name, session_id, turn_id, option_id):
        self.num_responses += 1

        if player_name in self.voted_players:
            return None

        elif room != self.room_code:
            raise ValueError("Room code does not match voting session")
            return None
        elif player_name not in self.voted_players:
            self.voted_players.append(player_name)        


        if self.num_players != self.num_responses:
            self.votes[option_id] += 1
        elif self.num_players < self.num_responses:

            raise ValueError("Number of responses exceeds number of players")
            return None
        else:
            max_votes = 0
            final_option = random.choice(list(self.votes.keys()))
            for option, vote in self.votes:
                if vote > max_votes:
                    max_votes = vote
                    final_option = option
    
            return final_option
        return None
