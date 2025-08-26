import api from "./api.js";

/**
 * Retrieves Scenario for the display
 * 
 * @returns {Promise<object>} The next scenario
 */
export const getScenario = async (year) => {
  const response = await api.get("/storyline/start", {
    params: { year }
  });
  return response.data;
};