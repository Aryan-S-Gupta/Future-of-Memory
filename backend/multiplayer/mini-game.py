import threading
import logging

logger = logging.getLogger(__name__)

# Global dictionary to store mini-game sessions
# Structure: {(room_code, turn_id): {"scores": {player_name: score}, "tied_players": [], "winner": None, "option_map": {player_name: option_id}}}
MINIGAMES = {}
LOCK = threading.Lock()


def start_minigame(room_code, turn_id, tied_players, option_map):
    """
    Initialize a mini-game for tied players.
    `option_map` maps each tied player to their original option choice.
    """
    with LOCK:
        MINIGAMES[(room_code, turn_id)] = {
            "scores": {},
            "tied_players": tied_players,
            "winner": None,
            "option_map": option_map
        }
    logger.info(f"Mini-game started for room {room_code}, turn {turn_id}, tied players: {tied_players}")


def submit_score(room_code, turn_id, player_name, score):
    """
    Submit a player's score for the mini-game.
    Returns:
        dict: {"status": "waiting"/"resolved", "winner": player_name, "winning_option": option_id, "scores": {...}}
    """
    key = (room_code, turn_id)
    with LOCK:
        if key not in MINIGAMES:
            return {"error": "Mini-game not found"}

        mg = MINIGAMES[key]
        mg["scores"][player_name] = score

        # Check if all tied players submitted scores
        if all(p in mg["scores"] for p in mg["tied_players"]):
            # Determine winner by highest score
            winner = max(mg["scores"].items(), key=lambda x: x[1])[0]
            mg["winner"] = winner
            winning_option = mg["option_map"].get(winner)
            logger.info(f"Mini-game resolved for room {room_code}, turn {turn_id}. Winner: {winner}, Option: {winning_option}")
            return {"status": "resolved", "winner": winner, "winning_option": winning_option, "scores": mg["scores"]}
        else:
            return {"status": "waiting", "scores": mg["scores"]}


def get_status(room_code, turn_id):
    """Poll current mini-game status"""
    key = (room_code, turn_id)
    with LOCK:
        if key not in MINIGAMES:
            return {"error": "Mini-game not found"}
        mg = MINIGAMES[key]
        return {
            "status": "resolved" if mg["winner"] else "waiting",
            "winner": mg["winner"],
            "scores": mg["scores"],
            "tied_players": mg["tied_players"],
            "option_map": mg["option_map"]
        }
