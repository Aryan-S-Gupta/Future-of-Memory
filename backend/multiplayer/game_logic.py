import logging
import random
from collections import Counter
import multiplayer.room_manager as rm
import threading
"""
Game logic for multiplayer sessions.

This module handles voting sessions, player management, and game state updates.

Classes:
    VotingSession: Manages voting sessions within a multiplayer room.
    
    Functions:
    - add_player(room_code, player_name): Add a player to a room.
    - join_room(room_code, player_name): Join an existing room.
    - remove_player(room_code, player_name): Remove a player from a room.
    - get_session_id(room_code): Retrieve the session ID for a room.
    - update_state(room_code, state): Update the game state for a room.
    - get_state(room_code): Get the current game state for a room.
"""
class VotingSession:

    def __init__(self, room_code, turn_id, vote_timeout=30):
        """
        Initialize a voting session for a specific room.
        Args:
            room_code (str): The room code for the voting session.
            turn_id (int): The current turn ID for the session.
            vote_timeout (int): Time in seconds to wait before ending the vote. 
        Attributes:
            - room_code (str): The room code for the voting session.
            - votes (dict): Tally of votes for each option.
            - turn_id (int): The current turn ID for the session.
            - num_responses (int): Number of players who have voted.
            - total_players (int): Total number of players in the room.
            - voted_players (list): List of players who have voted.
            - vote_timeout (int): Timeout duration for the voting session.
            - vote_timer (threading.Timer): Timer object for vote timeout.
            - inactive_players (set): Players who did not vote before timeout.
            - final_option (str): The option that won the vote.
            - lock (threading.Lock): Lock for thread-safe operations.
        """
        self.room_code = room_code
        self.votes = {}
        self.p_votes = {}
        self.turn_id = turn_id
        self.num_responses = 0
        self.total_players = len(rm.get_players(room_code))
        self.voted_players = []
        self.vote_timeout = vote_timeout
        self.vote_timer = self.vote_timer = threading.Timer(self.vote_timeout, self.end_voting)
        self.time_started = False
        self.inactive_players = set()
        self.final_option = None
        self.lock = threading.Lock()
        logging.info(f"VotingSession initialized for room {room_code} with {self.total_players} players.")


    def start_voting(self):
        """
        Initialize a voting session for a specific room.
        Args:
            room_code (str): The room code for the voting session.
            vote_timeout (int): Time in seconds to wait before ending the vote.
            
            Attributes:
            - votes (dict): Tally of votes for each option.
            - num_responses (int): Number of players who have voted.
            - total_players (int): Total number of players in the room.
            - voted_players (list): List of players who have voted.
            - vote_timeout (int): Timeout duration for the voting session.
            - vote_timer (threading.Timer): Timer object for vote timeout.
            - inactive_players (set): Players who did not vote before timeout.
            - final_option (str): The option that won the vote.
            - lock (threading.Lock): Lock for thread-safe operations.
        """
        with self.lock:
            """Start the voting session and initialize/reset all relevant attributes."""
            self.votes = {}
            self.voted_players = []
            self.num_responses = 0
            self.total_players = len(rm.get_players(self.room_code))
            self.inactive_players = set()
            self.final_option = None
            
            # Start timeout timer
            if self.vote_timer:
                self.vote_timer.cancel()

            logging.info(f"Voting started for room {self.room_code} with {self.total_players} players.")

            # Start global timer
            
            self.vote_timer.start()
            self.vote_timer = True

            logging.info(f"AFK timer started for {self.vote_timeout} seconds in room {self.room_code}")

    def is_timer_on(self):
        return self.vote_timer 

    def end_voting(self):
        """
        End the voting session, tally votes, and determine the final option.
        
        This method is called when the vote timeout expires.
        It tallies the votes, accounts for inactive players, and computes the final option.
        
        Attributes:
            - votes (dict): Tally of votes for each option.
            - num_responses (int): Number of players who have voted.
            - total_players (int): Total number of players in the room.
            - voted_players (list): List of players who have voted.
            - inactive_players (set): Players who did not vote before timeout.
            - final_option (str): The option that won the vote.
            - lock (threading.Lock): Lock for thread-safe operations.
        """
        with self.lock: 
            """Called when the vote timeout expires."""
            all_players = set(rm.get_players(self.room_code))
            self.inactive_players = all_players - set(self.voted_players)
            logging.info(f"Skipping votes for inactive players: {self.inactive_players} in room {self.room_code}")
            self.num_responses += len(self.inactive_players)

            final_option = self.compute_final_vote()
            logging.info(f"Voting session ended. Final option: {final_option}")

    
    def process_player_response(self, room, player_name, option_id):
        """
        Process a player's vote in the voting session.
        Args:
            room (str): The room code for the voting session.
            player_name (str): The name of the player casting the vote.
            option_id (str): The option ID the player is voting for.

        Attributes:
            - votes (dict): Tally of votes for each option.
            - num_responses (int): Number of players who have voted.
            - total_players (int): Total number of players in the room.
            - voted_players (list): List of players who have voted.
            - inactive_players (set): Players who did not vote before timeout.
            - final_option (str): The option that won the vote.
            - lock (threading.Lock): Lock for thread-safe operations.   
        
        Returns: str: The final option if voting is complete, None otherwise.
        """
        with self.lock:
            if room != self.room_code:
                raise ValueError("Room code does not match voting session")
        
            if player_name in self.voted_players:
                return None
        
            logging.info(f"Player {player_name} voted for option {option_id} in room {room}")  
            logging.info(f"Total players in room: {rm.get_players(room)}")
            # record the player's vote
            self.voted_players.append(player_name)
            self.p_votes[player_name] = option_id 
            self.num_responses += 1
            logging.info(f"Total responses: {self.num_responses}/{self.total_players}")

            # tally the vote
            if self.votes is None:
                return None
            self.votes[option_id] = self.votes.get(option_id, 0) + 1
            logging.info(f"Current votes tally: {self.votes}")

            # check if everyone voted early and end voting
            if self.num_responses >= self.total_players:
                if self.vote_timer:
                    self.vote_timer.cancel()
                self.final_option = self.compute_final_vote()
                return self.final_option
            return None
    
    def compute_final_vote(self):

        """Compute the final vote after all players have responded or timeout.
        Returns:
            str: The option ID that won the vote.
        
        Attributes:
            - votes (dict): Tally of votes for each option.
            - num_responses (int): Number of players who have voted.
            - total_players (int): Total number of players in the room.
            - voted_players (list): List of players who have voted.
            - inactive_players (set): Players who did not vote before timeout.
            - final_option (str): The option that won the vote.
            - lock (threading.Lock): Lock for thread-safe operations.
        """
        if not self.votes:
            return None

        final_option =random.choice(list(self.votes.keys()))
        if not self.votes:
            logging.info("No votes were cast. Selecting a random option or returning None.")
            return final_option

        # all players have voted, compute final option
        max_votes = -1
        for option, vote in self.votes.items():
            logging.info(f"Option {option} has {vote} votes")
            if vote > max_votes:
                max_votes = vote
                final_option = option
                logging.info(f"New leading option: {final_option} with {max_votes} votes") 
        # self.votes = {}
        # self.num_responses = 0
        # self.voted_players = []
        # self.inactive_players = set()
        if self.vote_timer:
            self.vote_timer.cancel()
            self.vote_timer = None
        logging.info(f"Final option selected: {final_option}") 
        # reset for next round
        return final_option

    def get_room_code(self):
        """Get the room code for this voting session.
        Returns:
            str: The room code associated with this voting session.
        Attributes: 
            - room_code (str): The room code for the voting session.    
        """
        return self.room_code    
    
    def set_room_code(self, room_code):
        """Set the room code for this voting session.
        Args:
            room_code (str): The room code to set for this voting session.
        Attributes:
            - room_code (str): The room code for the voting session.
        """
        self.room_code = room_code   
    
    def set_turn_id(self, turn_id):
        """Set the turn ID for this voting session.
        Args:
            turn_id (int): The turn ID to set for this voting session.
        Attributes:
            - turn_id (int): The current turn ID for the session.  
        """
        self.turn_id = turn_id      


    def get_turn_id(self):
        """Get the turn ID for this voting session.
        Returns:
            int: The turn ID associated with this voting session.
        Attributes:
            - turn_id (int): The current turn ID for the session.  
        """
        return self.turn_id
    
    def get_num_responses(self):
        """Get the number of players who have voted so far.
        Returns:
            int: The number of players who have voted.
        Attributes:
            - num_responses (int): Number of players who have voted.  
        """
        return self.num_responses       
    
    def get_total_players(self):
        """Get the total number of players in the room.
        Returns:
            int: The total number of players in the room.
        Attributes:
            - total_players (int): Total number of players in the room.  
        """
        return self.total_players   
    
    def get_voted_players(self):
        """Get the list of players who have voted so far.
        Returns:
            list: Names of players who have voted.
        Attributes:
            - voted_players (list): List of players who have voted.  
        """
        return self.voted_players   
    
    def get_inactive_players(self):
        """Get the list of players who did not vote before timeout.
        Returns:
            set: Names of players who did not vote.
        Attributes:
            - inactive_players (set): Players who did not vote before timeout.  
        """
        return self.inactive_players    
    
    def get_vote_timeout(self):
        """Get the vote timeout duration.
        Returns:
            int: The vote timeout duration in seconds.
        Attributes:
            - vote_timeout (int): Timeout duration for the voting session.  
        """
        return self.vote_timeout    
    def set_vote_timeout(self, vote_timeout):
        """Set the vote timeout duration.
        Args:
            vote_timeout (int): The vote timeout duration in seconds.
        Attributes:
            - vote_timeout (int): Timeout duration for the voting session.  
        """
        self.vote_timeout = vote_timeout    

    def get_vote_timer(self):
        """Get the vote timer object.
        Returns:
            threading.Timer: The timer object for the vote timeout.
        Attributes:
            - vote_timer (threading.Timer): Timer object for vote timeout.  
        """
        return self.vote_timer  
    
    def set_vote_timer(self, vote_timer):
        """Set the vote timer object.
        Args:
            vote_timer (threading.Timer): The timer object for the vote timeout.
        Attributes:
            - vote_timer (threading.Timer): Timer object for vote timeout.  
        """
        self.vote_timer = vote_timer    

    def get_num_votes(self):
        """Get the current tally of votes for each option.
        Returns:
            dict: Tally of votes for each option.
        Attributes:
            - votes (dict): Tally of votes for each option.  
        """
        return self.votes
    
    def get_p_votes(self):
        """Get the current votes cast by each player.
        Returns:
            dict: Mapping of player names to their voted option IDs.
        Attributes:
            - p_votes (dict): Mapping of player names to their voted option IDs.  
        """
        return self.p_votes        
    
    def reset_votes(self):
        """Reset the votes and voting state for a new round.
        This should be called before starting a new voting session.
        Attributes:
            - votes (dict): Tally of votes for each option.
            - num_responses (int): Number of players who have voted.
            - voted_players (list): List of players who have voted.
            - inactive_players (set): Players who did not vote before timeout.
            - final_option (str): The option that won the vote.
        """ 
        self.votes = {}
        self.p_votes = {} 
        self.voted_players = []
        self.num_responses = 0
        self.inactive_players = set()
        self.final_option = None
        if self.vote_timer:
            self.vote_timer.cancel()
            self.vote_timer = None
        logging.info(f"Voting state reset for room {self.room_code}")

    def add_player(self):
        """
        Increment the total number of players in the room.
        This should be called whenever a new player joins the room.  
        Attributes:
            - total_players (int): Total number of players in the room.
        """
        self.total_players += 1
        logging.info(f"Added a player. Total players now {self.total_players}")


    def remove_player(self):    
        """
        Decrement the total number of players in the room.
        This should be called whenever a player leaves the room.  
        Attributes:
            - total_players (int): Total number of players in the room.
        """
        if self.total_players > 0:
            self.total_players -= 1
            logging.info(f"Removed a player. Total players now {self.total_players}")
        else:
            logging.warning("Attempted to remove a player when total_players is already 0.")    

    
    def get_total_players(self):    
        """Get the total number of players in the room.
        Returns:
            int: The total number of players in the room.
        Attributes:
            - total_players (int): Total number of players in the room.  
        """
        return self.total_players


    def update_players(self):
        """
        Update the total number of players in the room.
        This should be called whenever players join or leave the room.  
        Attributes:
            - total_players (int): Total number of players in the room.
        """
        self.total_players = len(rm.get_players(self.room_code))
        logging.info(f"Updated total players to {self.total_players}")



    def get_final_option(self):
        """
        Get the final option selected after voting.
        Returns:
            str: The option ID that won the vote, or None if voting is still in progress.
        Attributes:
            - final_option (str): The option that won the vote. 

        """
        return self.final_option
    
    def get_vote_status(self):
        """Returns vote status including players who voted and total count.
        Returns:
            dict: {"num_responses": int, "players_voted": list, "total_players": int,
                     "final_option": str or None}   
        Attributes:
            - num_responses (int): Number of players who have voted.
            - voted_players (list): List of players who have voted.
            - total_players (int): Total number of players in the room.
            - final_option (str): The option that won the vote. 
        """
        return {
            "num_responses": self.num_responses,
            "players_voted": list(self.voted_players),
            "total_players": self.total_players,
            "final_option": self.final_option,
            "turn_id": self.turn_id
        }

    def has_finished(self):
        """Returns True if voting has finished."""
        return self.final_option is not None


    def get_current_votes(self):
        """
        Return current voting status for each player.
        Shows the option ID for players who voted,
        and 'Pending' for those who haven't yet.
        """
        all_players = set(rm.get_players(self.room_code))
        votes_so_far = {}

        for player in all_players:
            if player in self.voted_players:
                votes_so_far[player] = self.p_votes.get(player, None)
            else:
                votes_so_far[player] = "Pending"

        logging.debug(f"Vote status for room {self.room_code}: {votes_so_far}")
        return votes_so_far


# Global dictionary to manage voting sessions per room
VotingSessions = {}
