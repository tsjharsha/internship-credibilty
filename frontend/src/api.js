const API_URL = "http://127.0.0.1:5000";
// src/api.js
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});

export default api;
