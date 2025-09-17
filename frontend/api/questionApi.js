import api from "./api";


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
export const getQuestion = async(year) => {
  const response = await api.get("/storyline/question", {
    params: { year }
  })
  return response.data // extract only data of the payload
};

