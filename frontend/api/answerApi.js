import api from "./api";

/**
 * Send the user's choice for a given year.
 * 
 * @param {number|string} year - The current story year
 * @param {string} choice - The user's selected choice
 * @returns {Promise<object>} The result and next scenario/question
 */
export const submitChoice = async (year, choice) => {
  try {
    const response = await api.post("/storyline/result", {
      params: { year, choice }
    });
    return response.data;
  } catch (error) {
    console.error("Error submitting choice:", error);
    throw error;
  }
};
