import logging

logger = logging.getLogger(__name__)

# Store scores for single-player mini-game
# Structure: {player_name: score}
SINGLE_PLAYER_SCORES = {}

def submit_score_single(player_name: str, score: int):
    """
        Submit a player's score for the single-player memory game.
        
        Args:
            player_name (str): The name of the player submitting the score.
            score (int): The player's score to record.

        Returns:
            dict: A JSON-style dictionary indicating success or failure.
                Example (success):
                    {"status": "success", "player_name": "Alice", "score": 85}
                Example (error):
                    {"error": "Missing player_name or score"}
        """
    if not player_name or score is None:
        logger.warning("submit_score_single called with missing parameters")
        return {"error": "Missing player_name or score"}

    SINGLE_PLAYER_SCORES[player_name] = score
    logger.info(f"Score submitted: {player_name} -> {score}")
    return {"status": "success", "player_name": player_name, "score": score}

def get_scores():
    """
    Retrieve all submitted single-player scores.

    Returns:
        dict: A dictionary of all players and their corresponding scores.
                Example:
                    {
                        "Alice": 85,
                        "Bob": 72
                    }
    """
    return SINGLE_PLAYER_SCORES
