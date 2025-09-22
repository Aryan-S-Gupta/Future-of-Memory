import api from "./api";
/**
 * Fetch scenario for given year in a room.
 * @param {string} roomCode
 * @param {number} year
 * @returns {Promise<object>} Scenario data.
 */
export const getScenario = async (roomCode, year) => {
const response = await api.get(`/storyline/start`, { params: { year, roomCode } });
  return response.data;
};

/**
 * Fetch question for given year in a room.
 * @param {string} roomCode
 * @param {number} year
 * @returns {Promise<object>} Question data.
 */
export const getQuestion = async (roomCode, year) => {
  const response = await api.get(`/storyline/question`, { params: { year, roomCode } })
  return response.data;
};

/**
 * Submit a player's choice.
 * @param {string} roomCode
 * @param {string} playerName
 * @param {number} year
 * @param {string} choice - Option selected by the player.
 * @returns {Promise<object>} Submission result (and maybe updated state).
 */
export const submitChoice = async (roomCode, playerName, year, choice) => {
  const response = await api.post(`/storyline/choice`, { playerName, year, choice, roomCode });
  return response.data;
};

