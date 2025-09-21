import random
from collections import Counter

def singleplayer_result(year, choice, story_data):
    entry = next((item for item in story_data if str(item["year"]) == str(year)), None)
    if not entry:
        return {"error": "Year not found", "status": 404}

    result = entry.get("options", {}).get(choice.lower())
    if not result:
        return {"error": f"No result found for choice '{choice}'", "status": 404}

    return {
        "year": entry["year"],
        "choice": choice,
        "result": result,
        "next_year": entry["year"] + 1,
    }

def multiplayer_result(room, player_name, choice):
    player = room["players"].get(player_name)
    if not player:
        return {"error": f"No player named {player_name} in room"}
    
    player["last_choice"] = choice

    all_answered = all(p.get("last_choice") for p in room["players"].values())
    outcome = None
    if all_answered:
        votes = [p["last_choice"] for p in room["players"].values()]
        count = Counter(votes)
        max_votes = max(count.values())
        top_choices = [c for c, v in count.items() if v == max_votes]
        outcome = random.choice(top_choices)  # break ties randomly

        # Move room to next year
        room["current_year"] += 1
        # Clear last choices
        for p in room["players"].values():
            p["last_choice"] = None

    return {"all_answered": all_answered, "outcome": outcome, "current_year": room["current_year"]}
