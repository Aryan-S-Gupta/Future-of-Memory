import api from "./api";

/**
 * List all available rooms.
 * @returns {Promise<object[]>} Array of room objects.
 */
export const listRooms = async () => {
  const response = await api.get("/multiplayer/rooms");
  return response.data;
};

/**
 * Create a new room with the given player as host.
 * @param {string} playerName - The name of the player creating the room.
 * @returns {Promise<object>} Newly created room data.
 */
export const createRoom =  async (playerName) => {
  const response = await api.post("/multiplayer/create", { playerName });
  return response.data
};

/**
 * Join an existing room.
 * @param {string} roomCode - Code of the room to join.
 * @param {string} playerName - The player's chosen name.
 * @returns {Promise<object>} Room state after joining.
 */
export const joinRoom = async (roomCode, playerName) => {
  const response = await api.post(`/multiplayer/${roomCode}/join`, { playerName });
  return response.data;
};

/**
 * Get the current room state (players, choices, etc.)
 * @param {string} roomCode - Room identifier.
 * @returns {Promise<object>} Room state.
 */
export const getRoomState = async (roomCode) => {
  const response = await api.get(`/multiplayer/${roomCode}/state`);
  return response.data;
};