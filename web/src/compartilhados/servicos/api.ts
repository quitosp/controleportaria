import axios from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5270";

export const api = axios.create({
  baseURL,
  withCredentials: false,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("auth.token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (typeof window !== "undefined" && err?.response?.status === 401) {
      localStorage.removeItem("auth.token");
      if (window.location.pathname !== "/login") window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);
