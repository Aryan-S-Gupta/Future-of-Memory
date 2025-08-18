import api from "./api"
// Fetch Questions
export const getQuestion = async () => {
  const response = await api.get("/question");
  return response.data;
};
