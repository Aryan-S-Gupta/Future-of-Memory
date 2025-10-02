import api from "./api"

export const createSession = async () => {
  const response = await api.get("/create_session");
  return response.data;
};

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
  return res.data;
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
export const getQuestion = async (session_id) => {
  console.log("called question api for session:", session_id);
  const res = await api.get(`/storyline/${session_id}/question`);
  console.log("got output:", res.data);  // prints the actual object
  console.log("question:", res.data.data.question);
  console.log("options:", res.data.data.options);

  return res.data.data; // { message, data: { turn_id, year, question, options } }
};


/**
 * Fetches an image from the backend API.
 *
 * - Uses the pre-configured Axios instance (`api`) to make the request.
 * - Sends a GET request to `/image` endpoint.
 * - Returns only the response data (`res.data`) instead of the entire Axios response object.
 *
 * @async
 * @function getImage
 * @returns {Promise<any>} The data returned from the `/image` endpoint.
 *
 * Example usage:
 * const imageData = await getImage();
 * console.log(imageData);
 */
export const getImage = async () => {
  const res = await api.get("/image");
  return res.data; // extract only data of the payload
};

/**
 * Send the user's choice for a given year.
 * 
 * @param {number|string} year - The current story year
 * @param {string} choice - The user's selected choice
 * @returns {Promise<object>} The result and next scenario/question
 */
export const submitChoice = async (session_id, turn_id, year, option_id) => {
  const res = await api.get(
    `/storyline/start/${session_id}/${turn_id}/${year}/${option_id}`
  );
  return res.data; // { scenario, image, ...
}

export const getFunFacts = async () => {
  const res = await api.get("/rag/fun_facts");
  return res.data; // array of { fact, link, link_text }
}