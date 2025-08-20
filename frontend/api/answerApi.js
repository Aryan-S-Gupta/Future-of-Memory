import api from "./api";

// Send selected choice
export const sendChoice = async (year, choice) => {
  const response = await api.post("/storyline/choice", { year, choice });
  return response.data;
};
