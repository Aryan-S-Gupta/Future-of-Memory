import logging
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
        
        logging.debug(f"Player {player_name} voted for option {option_id} in room {room}")  
        logging.debug(f"Total players in room: {rm.get_players(room)}")
        self.voted_players.append(player_name)
        self.num_responses += 1
        logging.debug(f"Total responses: {self.num_responses}/{self.total_players}")

         # tally the vote

        if option_id not in self.votes:
            self.votes[option_id] = 0
        self.votes[option_id] += 1
        logging.debug(f"Current votes tally: {self.votes}")

         # check if all players have voted

        if self.num_responses < self.total_players:
            return None

        # all players have voted, compute final option
        max_votes = -1
        final_option = random.choice(list(self.votes.keys()))
        for option, vote in self.votes.items():
            logging.debug(f"Option {option} has {vote} votes")
            if vote > max_votes:
                max_votes = vote
                final_option = option
                logging.debug(f"New leading option: {final_option} with {max_votes} votes") 
        self.num_responses = 0
        self.votes = {}
        self.voted_players = []
        logging.debug(f"Final option selected: {final_option}") 
        # reset for next round
        return final_option

    def update_players(self):
        self.total_players = len(rm.get_players(self.room_code))
        logging.debug(f"Updated total players to {self.total_players}")