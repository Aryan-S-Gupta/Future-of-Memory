import api from "./api";

/**
 * List all available rooms.
 * @returns {Promise<object[]>} Array of room objects.
 */
export const listRooms = async () => {
  const response = await api.get("/rooms");
  return response.data;
};

/**
 * Create a new room with the given player as host.
 * @param {string} host - The name of the player creating the room.
 * @returns {Promise<object>} Newly created room data.
 */
export const createRoom =  async (host, mode) => {
  const response = await api.post("/create", { host, mode });
  return response.data
};

/**
 * Join an existing room.
 * @param {string} roomCode - Code of the room to join.
 * @param {string} playerName - The player's chosen name.
 * @returns {Promise<object>} Room state after joining.
 */
export const joinRoom = async (roomCode, playerName) => {
  const response = await api.post(`/join`, { roomCode, playerName });
  return response.data;
};

/**
 * Leave the current room player is in
 * @param {String} roomCode - Code of the room to leave
 * @param {*} playerName - The player's chosen name.
 * @returns {Promise<object>} Room state after leave
 */
export const leaveRoom = async (roomCode, playerName) => {
  console.log(roomCode)
const response = await api.get(`/leave`, {
    params: { roomCode, playerName }
  });
  return response.data;
}
/**
 * Get the current room state (players, choices, etc.)
 * @param {string} roomCode - Room identifier.
 * @returns {Promise<object>} Room state.
 */
export const getRoomState = async (roomCode) => {
  const response = await api.get(`/${roomCode}/state`);
  return response.data;
};

export const checkGameStarted = async (roomCode) => {
  const res = await api.get(`/check_game_started/${roomCode}`);
  return res;
}

export const getHostName = async (roomCode) => {
  const res = await api.get(`/host/${roomCode}`);
  return res;
}

export const startGame = async (roomCode) => {
  const res = await api.get(`start_game/${roomCode}`);
  return res;
}

export const isRoomEmpty = async (roomCode) => {
  const res = await api.get(`/room_empty/${roomCode}`);
  return res;
}