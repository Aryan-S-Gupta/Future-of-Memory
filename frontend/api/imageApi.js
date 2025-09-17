import api from "./api"

export const getImage = async () => {
  const res = await api.get("/image");
  return res.data;
};
