import api from "./api.js";

/**
 * Fetches the scenario for a given year from the backend.
 *
 * - Uses the pre-configured Axios instance (`api`).
 * - Sends a GET request to the `/storyline/start` endpoint.
 * - Passes the `year` as a query parameter to get the appropriate scenario.
 * - Returns only the response data.
 *
 * @async
 * @function getScenario
 * @param {number} year - The current year for which to fetch the scenario.
 * @returns {Promise<object>} The scenario object containing scenario text and metadata.
 *
 * Example usage:
 * const scenario = await getScenario(2035);
 * console.log(scenario.scenario);
 */
export const getScenario = async (year) => {
  const response = await api.get("/storyline/start", {
    params: { year }
  });
  return response.data;
};