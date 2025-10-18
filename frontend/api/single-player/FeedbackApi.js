import api from "./api";

export const submitFeedback = async (payload) => {
  const res = await api.post(`/feedback`, payload);
  return res.data;
};

export default api;
