import api from "./api";
import { getRoomState } from "./RoomManagementApi";

export const startPrerender = async (session_id, year) => {
  const res = await api.get("/start_prerender", { params: { session_id, year } });
  return res.data; // { status: "generation_started" }
};

/**
 * Fetches the scenario for a given year from the backend.
 *
 * - Uses the pre-configured Axios instance (`api`).
 * - Sends a GET request to the `/storyline/start` endpoint.
 * - Passes the `year` as a query parameter to get the appropriate scenario.
 * - Returns only the response data.
 *
 * @async
 * @function getScenarioAndImage
 * @param {number} year - The current year for which to fetch the scenario.
 * @returns {Promise<object>} The scenario object containing scenario text and metadata.
 *
 * Example usage:
 * const scenario = await getScenario(2035);
 * console.log(scenario.scenario);
 */
export const getScenarioAndImage = async (session_id, turn_id, year, option_id) => {
  const res = await api.post(`/storyline/start/${session_id}/${turn_id}/${year}/${option_id}`);
  return res;
};

export const getVotingInfo = async (roomCode, turn_id) => {
  const res = await api.get(`votes/${roomCode}/${turn_id}`);
  return res;
}
/**
 * Fetches the question for a given year from the backend.
 *
 * - Uses the pre-configured Axios instance (`api`).
 * - Sends a GET request to the `/storyline/question` endpoint.
 * - Passes the `year` as a query parameter to get the appropriate question.
 * - Returns only the response data.
 *
 * @async
 * @function getQuestion
 * @param {number} year - The current year for which to fetch the question.
 * @returns {Promise<object>} The question object containing the question text and options.
 *
 * Example usage:
 * const question = await getQuestion(2035);
 * console.log(question.question);
 * console.log(question.options);
 */
export async function getQuestion(sessionId, roomCode, turn_id, year) {
  try {
    const res = await api.get(`/storyline/${sessionId}/question/${roomCode}/${turn_id}/${year}`);
    console.log("got output: " + res)
    console.log(res.data)
    return res.data;
  } catch (err) {
    return null;
  }
}
/**
 * Submit a player's choice.
 * @param {string} roomCode
 * @param {string} playerName
 * @param {number} year
 * @param {string} choice - Option selected by the player.
 * @returns {Promise<object>} Submission result (and maybe updated state).
 */

export const submitChoice = async (playerName, roomCode, session_id, turn_id, year, option_id) => {
  try {
  const res = await api.get(
    `/storyline/choice/${session_id}/${turn_id}/${year}/${option_id}/${roomCode}`, { params: { playerName }}
  );
  return res.data; // { scenario, image, ...
} catch (err) {
  return null;
}
}

export const getFunFacts = async () => {
  const res = await api.get("/fun_facts");
  return res.data; // array of { fact, link, link_text }
}


/**
 * Submit a single-player memory game score to the backend.
 *
 * @param {string} playerName - Name of the player.
 * @param {number} score - Score achieved in the mini-game.
 * @returns {Promise<object>} The response from the backend.
 *
 * Example usage:
 * const result = await submitMemoryScore("Alice", 85);
 */
export const submitMemoryScore = async (playerName, score) => {
  const res = await api.post("/mini-game/submit_score_single", { player_name: playerName, score });
  return res.data; // { status: "success", player_name, score }
};

/**
 * Optional: Retrieve all submitted single-player scores.
 */
export const getMemoryScores = async () => {
  const res = await api.get("/mini-game/scores");
  return res.data.scores; // { player_name: score, ... }
};


/**
 * Submit multiplayer minigame score for tie-break resolution.
 * @param {string} playerName
 * @param {string} roomCode
 * @param {number} turnId
 * @param {number} score
 */
export const submitTiebreakScore = async (playerName, roomCode, turnId, score) => {
  const res = await api.post("/mini-game/submit_tiebreak_score", {
    room_code: roomCode,
    turn_id: turnId,
    player_name: playerName,
    score,
  });
  return res.data;
};

/**
 * Get current tie-break status.
 * Returns: { tie_mode, tie_players, tie_scores, final_option }
 */
export const getTiebreakStatus = async (roomCode, turnId) => {
  const res = await api.get(`/mini-game/tiebreak_status/${roomCode}/${turnId}`);
  return res.data;
};
