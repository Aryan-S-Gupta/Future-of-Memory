import api from "./api";

/**
 * Retrieves Questions for the display
 * 
 * @returns {Promise<object>} The next question
 */export const getQuestion = async(year) => {
  const response = await api.get("/storyline/question", {
    params: { year }
  })
  return response.data
};

