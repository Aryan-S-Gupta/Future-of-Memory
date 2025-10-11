import logging

from django.http import JsonResponse
from shared.models import Session, Option, Turn

"""
Global Dictionary to store all multiplayer rooms.
Key: room_code (string), Value: room details (dict)
"""
rooms = {}  
""" 
Maps room codes to session IDs 
"""
room_sessions = {}

# Room lifecyle
def create_room(host_name, mode):
    """
    Create a new room with a unique room code with host as a player.
    This function can be used when the host is also a player 
    For exmaple, in kiosks or peer - peer without the interaction with host.
    
    Args:
        host_name (str): Name of the player creating the room.
        mode (str): the mode (eg host or peer-peer mode they are playing)

    Attr:s:
        rooms (dict): Global dictionary storing all rooms.
        
    Returns:
        str: The room code of the newly created room.
    """
    # Generate a room code based on current number of rooms, padded to 4 digits
    room_code = str(len(rooms) + 1).zfill(4)
    session = Session.objects.create()
    logging.info(f'session id created: {session.id}')
    room_sessions[room_code] = session.id

    # Initialize room data: host, list of players, and game state
    rooms[room_code] = {
        "host": host_name,
        "players": [host_name],  # host is the first player
        "mode": mode,
        "state": {
            "turn_id": -1,
            "year": 2035
        },
        "game_started": False
    }   
    logging.info(f"Room created with code {room_code} by host {host_name}")
    logging.info(f'Current rooms: {rooms}')
    return room_code, session.id

def create_host_room(host_name, mode): 
    """
    Creates a new room without the host as a player. 
    This function can be used while playing in server-host mode

    Args:
        host_name (str); Name of the player creating the room.

    Attrs:
        room (dict): glocal dictionary storing all rooms.

    Returns: 
        str: The room code of the newly created room.
    """
    room_code = str(len(rooms) + 1).zfill(4)
    session = Session.objects.create()
    logging.info(f'session if created: {session.id}')
    room_sessions[room_code] = session.id
    rooms[room_code] = {
        "host": host_name,
        "players": [],  # don't add the host 
        "mode": mode,
        "state": {
            "turn_id": -1,
            "year": 2035
        },
        "game_started": False      
    }
    logging.info(f"Host room created with code {room_code} by host {host_name}")
    logging.info(f'Current rooms: {rooms}')
    return room_code, session.id

def join_room(room_code, player_name):
    """
    Add a player to an existing room.
    
    Args:
        room_code (str): The room code to join.
        player_name (str): Name of the player joining.
        
    Returns:
        bool: True if successful, False if room doesn't exist.
    """
    if not room_exists(room_code):
        logging.warning(f'Join failed: room {room_code} not found.')
        return False
    
    elif player_in_room_exists(room_code, player_name):
        logging.info(f"{player_name} is already in room {room_code}.")
        return True
    
    else:
        add_player(room_code, player_name)
        logging.info(f'Player {player_name} joined room {room_code}')
        return True

def destroy_room(room_code):
    """
    Delete a room and all its data.
    
    Args:
        room_code (str): The room code to delete.
    Returns:
        bool: True if deletion was successful, False if room doesn't exist. 
    """
    if not room_exists(room_code):
        logging.warning(f'Destroy failed: room {room_code} not found.')
        return False
    
    else:
        del rooms[room_code]
        logging.info(f'Room {room_code} has been destroyed')
        return True
    
def destroy_all_rooms():
    """
    Force clear all rooms (useful during shutdown or testing).
    """
    rooms.clear()
    room_sessions.clear()
    logging.warning("All rooms have been cleared.")


def room_exists(room_code):
    """
    Check if a room with the given code exists.

    Args:
        room_code (str): The room code to check.

    Returns:
        bool: True if room exists, False otherwise."""
    return room_code in rooms


def leave_room(room_code, player_name):
    """
    Handle a player leaving a room. If the room becomes empty, destroy it.
    
    Args:
        room_code (str): The room code to leave.
        player_name (str): Name of the player leaving.
    
    Returns:
        bool: True if successful, False if room or player doesn't exist.
    """
    if remove_player(room_code, player_name):
        if get_player_count(room_code) == 0:
            destroy_room(room_code)

        elif get_host(room_code) == player_name:
            destroy_room(room_code)
        return True
    return False

def get_mode(room_code): 
    return rooms[room_code]["mode"]


def set_mode(room_code, mode):
    if not room_exists(room_code):
        return False 
    rooms[room_code]["mode"] = mode
    return True


def is_game_started(room_code):
    if not room_exists(room_code):
        return False 
    return get_room(room_code)["game_started"] == True
    
def set_game_started(room_code): 
    if not room_exists(room_code):
        return False 
    get_room(room_code)["game_started"] = True 

    
# Core Accessors
def get_room_codes():
    """
    Get a list of all existing room codes.
    
    Returns:
        list: Room codes as strings.
    """
    logging.info(f'Fetching all room codes are {rooms.keys()}')
    return list(rooms.keys())

def get_rooms():
    """
    Retrieve the full dictionary of rooms.
    
    Returns:
        dict: All rooms with their data.
    """
    return rooms

def get_room(room_code):
    """
    Retrieve details of a specific room by its code.
    
    Args:
        room_code (str): The room code to query.
    
    Returns:
        dict: Details of the room, or None if not found."""
    return rooms.get(room_code)

# Player Management
def get_host(room_code):
    """
    Get the host of a specific room.
    
    Args:
        room_code (str): The room code to query.
        
    Returns:
        str: Name of the host player, or None if room not found.
    """
    if room_code in rooms:
        return rooms[room_code]["host"]
    return None

def set_host(room_code, player_name):
    """
    Set a new host for a specific room.
    
    Args:
        room_code (str): The room code to update.
        player_name (str): Name of the new host player.
    
    Returns:
        bool: True if successful, False if room doesn't exist.
    """
    if room_code in rooms:
        rooms[room_code]["host"] = player_name
        return True
    return False

def is_host(room_code, player_name):
    """
    Check if a given player is the host of a specific room.
    
    Args:
        room_code (str): The room code to query.
        player_name (str): Name of the player to check.
    
    Returns:
        bool: True if player is the host, False otherwise.
    """
    if room_code in rooms:
        return rooms[room_code]["host"] == player_name
    return False

def player_in_room_exists(room_code, player_name):  
    """
    Check if a player is already in a specific room.
    
    Args:
        room_code (str): The room code to query.
        player_name (str): Name of the player to check.
    
    Returns:
        bool: True if player is in the room, False otherwise.
    """
    if room_exists(room_code):
        return player_name in rooms[room_code]["players"]
    logging.info("player does not exist in the room")
    return False

def get_players(room_code):
    """
    Get the list of players in a specific room.
    
    Args:
        room_code (str): The room code to query.
        
    Returns:
        list: Names of players in the room.
    """
    logging.info(f'Fetching players in room {rooms}')
    logging.info(f'Fetching players in room {room_code} which has players {rooms[room_code]["players"]}')
    return rooms[room_code]["players"]

def get_player_count(room_code):
    """
    Return the number of players currently in a room.
    
    Args:
        room_code (str): The room code to query.
    
    Returns:
        int: Number of players in the room.
    """
    if room_code in rooms:
        return len(rooms[room_code]["players"])
    return 0

def add_player(room_code, player_name):
    """
    Add a player to a room without checks.
    
    Args:
        room_code (str): The room code to join.
        player_name (str): Name of the player joining.
        
    Returns:
        bool: True if successful, False if room doesn't exist.
    """
    if not room_exists(room_code):
        logging.warning(f'Add failed: room {room_code} not found.')
        return False
    
    else:
        rooms[room_code]["players"].append(player_name)
        logging.info(f'Player {player_name} added to room {room_code}')
        return True


def remove_player(room_code, player_name):
    """ 
    Remove a player from a room.
    
    Args:
        room_code (str): The room code to leave.
        player_name (str): Name of the player leaving.

    Returns:
        bool: True if successful, False if room or player doesn't exist.
    """
    if not room_exists(room_code):
        logging.warning(f'Remove failed: room {room_code} not found.')
        return False

    if player_in_room_exists(room_code, player_name):
        rooms[room_code]["players"].remove(player_name)
        logging.info(f'Player {player_name} removed from room {room_code}')
        return True
    return False

def transfer_host(room_code, new_host):
    """
    Assign a new host for a room if the current one leaves.
    Args:
        room_code (str): The room code to update.
        new_host (str): Name of the new host player.
    Returns:
        bool: True if successful, False if room or new host doesn't exist.
    """
    if room_exists(room_code) and player_in_room_exists(room_code, new_host):
        old_host = rooms[room_code]["host"]
        set_host(room_code, new_host)
        logging.info(f"Host changed from {old_host} to {new_host} in room {room_code}")
        return True
    return False

# Room State Management 
def get_session_id(room_code):
    """
    Retrieve the session ID associated with a room code.
    
    Args:
        room_code (str): The room code to query.
        
    Returns:
        int: The session ID linked to the room.
    """
    return room_sessions.get(room_code)

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

def reset_state(room_code):
    """Reset the room's game state to defaults."""
    if room_code in rooms:
        rooms[room_code]["state"] = {"turn_id": -1, "year": 2035}
        logging.info(f"Room {room_code} state reset.")
        return True
    return False


# Debug / Utility 
def room_summary(room_code):
    """
    Return a quick summary of a room for debuging or display.
    """
    if room_code not in rooms:
        return None

    return {
        "room_code": get_room(room_code),
        "host": get_host(),
        "players": get_player_count(room_code),
        "session_id": get_session_id(room_code),
        "state": get_state(room_code)
    }

def log_all_rooms():
    """Logs a structured view of all rooms."""
    for code, data in rooms.items():
        logging.info(f"Room {code}: Host={data['host']}, Players={data['players']}, State={data['state']}")
