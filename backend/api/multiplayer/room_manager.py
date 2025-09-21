
rooms = {}  

def create_room(host_name):
    room_code = str(len(rooms) + 1)
    rooms[room_code] = {
        "host": host_name,
        "players": [host_name], 
        "state": {}, 
    }
    return room_code

def get_rooms():
    return rooms.keys()

def get_players(room_code):
    return rooms[room_code]["players"]

def join_room(room_code, player_name):
    if room_code in rooms:
        rooms[room_code]["players"].append(player_name)
        return True
    return False

def update_state(room_code, state):
    if room_code in rooms:
        rooms[room_code]["state"] = state
        return True
    return False

def get_state(room_code):
    return rooms.get(room_code).get("state")
