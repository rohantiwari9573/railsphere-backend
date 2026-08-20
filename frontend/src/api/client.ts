import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("railsphere_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Strip empty-string/null/undefined query params rather than send
  // them literally -- e.g. an empty search box would otherwise send
  // `search=`, which fails the backend's min_length=1 validation.
  if (config.params) {
    const cleaned: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(config.params)) {
      if (value !== "" && value !== null && value !== undefined) {
        cleaned[key] = value;
      }
    }
    config.params = cleaned;
  }

  return config;
});
