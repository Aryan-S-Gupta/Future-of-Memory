
# Dictionary to store all multiplayer rooms.
# Key: room_code (string), Value: room details (dict)
rooms = {}  


def create_room(host_name):
    """
    Create a new room with a unique room code.
    
    Args:
        host_name (str): Name of the player creating the room.
        
    Returns:
        str: The room code of the newly created room.
    """
    # Generate a room code based on current number of rooms, padded to 4 digits
    room_code = str(len(rooms) + 1).zfill(4)

    # Initialize room data: host, list of players, and game state
    rooms[room_code] = {
        "host": host_name,
        "players": [host_name],  # host is the first player
        "state": {},             # placeholder for game state
    }

    return room_code

def get_room_codes():
    """
    Get a list of all existing room codes.
    
    Returns:
        list: Room codes as strings.
    """
    return list(rooms.keys())

def get_rooms():
    """
    Retrieve the full dictionary of rooms.
    
    Returns:
        dict: All rooms with their data.
    """
    return rooms

def get_players(room_code):
    """
    Get the list of players in a specific room.
    
    Args:
        room_code (str): The room code to query.
        
    Returns:
        list: Names of players in the room.
    """
    return rooms[room_code]["players"]

def join_room(room_code, player_name):
    """
    Add a player to an existing room.
    
    Args:
        room_code (str): The room code to join.
        player_name (str): Name of the player joining.
        
    Returns:
        bool: True if successful, False if room doesn't exist.
    """
    if room_code in rooms:
        rooms[room_code]["players"].append(player_name)
        return True
    return False

def update_state(room_code, state):
    """
    Update the game state for a specific room.
    
    Args:
        room_code (str): The room code to update.
        state (dict): The new game state.
        
    Returns:
        bool: True if update was successful, False if room doesn't exist.
    """
    if room_code in rooms:
        rooms[room_code]["state"] = state
        return True
    return False

def get_state(room_code):
    """
    Retrieve the current game state for a specific room.
    
    Args:
        room_code (str): The room code to query.
        
    Returns:
        dict: The current state of the room.
    """
    return rooms.get(room_code).get("state")



