import api from "./api";


export const getStory = async () => {
  const response = await api.get("/story");
  return res.data;
};
