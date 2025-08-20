// Fetch story background for a specific year
export const getScenario = async (year) => {
  const response = await api.get("/storyline/start", {
    params: { year }
  });
  return response.data;
};