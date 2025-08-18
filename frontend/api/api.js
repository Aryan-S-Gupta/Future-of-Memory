import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api", //subjected to change based on backend localhost
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
