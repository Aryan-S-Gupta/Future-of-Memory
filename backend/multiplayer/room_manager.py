import logging

from django.http import JsonResponse
from shared.models import Session, Option, Turn
# Dictionary to store all multiplayer rooms.
# Key: room_code (string), Value: room details (dict)
rooms = {}  
room_sessions = {}  # Maps room codes to session IDs


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
    session = Session.objects.create()
    logging.debug(f'session id created: {session.id}')
    room_sessions[room_code] = session.id

    # Initialize room data: host, list of players, and game state
    rooms[room_code] = {
        "host": host_name,
        "players": [host_name],  # host is the first player
        "state": -1,             # placeholder for game state
    }   
    logging.info(f"Room created with code {room_code} by host {host_name}")
    logging.info(f'Current rooms: {rooms}')
    return room_code, session.id


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
        logging.info(f'Player {player_name} joined room {room_code}')
        return True
    return False

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

def destroy_room(room_code):
    """
    Delete a room and all its data.
    
    Args:
        room_code (str): The room code to delete.
    Returns:
        bool: True if deletion was successful, False if room doesn't exist. 
    """
    if room_code in rooms:
        del rooms[room_code]
        logging.info(f'Room {room_code} has been destroyed')
        return True
    return False