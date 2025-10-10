import logging

logger = logging.getLogger(__name__)

# Store scores for single-player mini-game
# Structure: {player_name: score}
SINGLE_PLAYER_SCORES = {}

def submit_score_single(player_name: str, score: int):
    """
    Submit a player's score for the single-player memory game.
    """
    if not player_name or score is None:
        logger.warning("submit_score_single called with missing parameters")
        return {"error": "Missing player_name or score"}

    SINGLE_PLAYER_SCORES[player_name] = score
    logger.info(f"Score submitted: {player_name} -> {score}")
    return {"status": "success", "player_name": player_name, "score": score}

def get_scores():
    """
    Retrieve all submitted scores.
    """
    return SINGLE_PLAYER_SCORES
