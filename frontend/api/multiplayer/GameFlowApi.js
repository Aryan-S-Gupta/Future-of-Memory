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
export const getQuestion = async (session_id, roomCode, turn_id) => {
  console.log("called question api for session:", session_id);
  const res = await api.get(`/storyline/${session_id}/question/${roomCode}/${turn_id}`);
  console.log("got output:", res.data);  // prints the actual object
  console.log("question:", res.data.data.question);
  console.log("options:", res.data.data.options);

  return res.data.data; // { message, data: { turn_id, year, question, options } }
};

/**
 * Submit a player's choice.
 * @param {string} roomCode
 * @param {string} playerName
 * @param {number} year
 * @param {string} choice - Option selected by the player.
 * @returns {Promise<object>} Submission result (and maybe updated state).
 */

export const submitChoice = async (playerName, roomCode, session_id, turn_id, year, option_id) => {
  const res = await api.get(
    `/storyline/choice/${session_id}/${turn_id}/${year}/${option_id}/${roomCode}`, { params: { playerName }}
  );
  return res; // { scenario, image, ...
}

export const getFunFacts = async () => {
  const res = await api.get("/fun_facts");
  return res.data; // array of { fact, link, link_text }
}