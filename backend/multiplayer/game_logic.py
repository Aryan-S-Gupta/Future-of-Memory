import logging
import random
from collections import Counter
import multiplayer.room_manager as rm
import threading
class VotingSession:

    def __init__(self, room_code, vote_timeout=30):
        self.room_code = room_code
        self.votes = {}
        self.num_responses = 0
        self.total_players = len(rm.get_players(room_code))
        self.voted_players = []
        self.vote_timeout = vote_timeout
        self.vote_timer = None
        self.inactive_players = set()
        self.final_option = None
        self.lock = threading.Lock()

    def start_voting(self):

        with self.lock:
            """Start the voting session and the global timer."""
            self.votes = {}
            self.voted_players = []
            self.num_responses = 0
            self.total_players = len(rm.get_players(self.room_code))
            self.inactive_players = set()

            logging.info(f"Voting started for room {self.room_code} with {self.total_players} players.")

            # Start global timer
            self.vote_timer = threading.Timer(self.vote_timeout, self.end_voting)
            self.vote_timer.start()
            logging.debug(f"AFK timer started for {self.vote_timeout} seconds in room {self.room_code}")

    def end_voting(self):
        with self.lock: 
            """Called when the vote timeout expires."""
            all_players = set(rm.get_players(self.room_code))
            self.inactive_players = all_players - set(self.voted_players)
            logging.info(f"Skipping votes for inactive players: {self.inactive_players} in room {self.room_code}")
            self.num_responses += len(self.inactive_players)

            final_option = self.compute_final_vote()
            logging.info(f"Voting session ended. Final option: {final_option}")

    
    def process_player_response(self, room, player_name, option_id):
        with self.lock:
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

            self.votes[option_id] = self.votes.get(option_id, 0) + 1
            logging.debug(f"Current votes tally: {self.votes}")

            # check if everyone voted early and end voting
            if self.num_responses >= self.total_players:
                if self.vote_timer:
                    self.vote_timer.cancel()
                return self.compute_final_vote()
            return None
    
    def compute_final_vote(self):

        """Compute the final vote after all players have responded or timeout."""

        if self.num_responses < self.total_players:
            return None
        
        
        final_option =random.choice(list(self.votes.keys()))
        if not self.votes:
            logging.warning("No votes were cast. Selecting a random option or returning None.")
            return final_option

        # all players have voted, compute final option
        max_votes = -1
        for option, vote in self.votes.items():
            logging.debug(f"Option {option} has {vote} votes")
            if vote > max_votes:
                max_votes = vote
                final_option = option
                logging.debug(f"New leading option: {final_option} with {max_votes} votes") 
        self.votes = {}
        self.num_responses = 0
        self.voted_players = []
        self.inactive_players = set()
        if self.vote_timer:
            self.vote_timer.cancel()
            self.vote_timer = None
        logging.debug(f"Final option selected: {final_option}") 
        # reset for next round
        return final_option

    def update_players(self):
        self.total_players = len(rm.get_players(self.room_code))
        logging.debug(f"Updated total players to {self.total_players}")