import api from "./api";


export const createRoom = (host) => api.post("multiplayer/create", { host });
export const listRooms = () => mpApi.get("multiplayer/rooms");
export const joinRoom = (roomCode, playerName) =>
  api.post("multiplayer/join", { room_code: roomCode, name: playerName });
export const getRoomState = (roomCode) =>
  api.get(`/room_state?room_code=${roomCode}`);

export default api;
