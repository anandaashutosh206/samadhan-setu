import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({ baseURL: API_URL });

const TOKEN_KEY = "samadhan_access_token";
const REFRESH_KEY = "samadhan_refresh_token";

export function getTokens() {
  if (typeof window === "undefined") return { access: null, refresh: null };
  return {
    access: window.localStorage.getItem(TOKEN_KEY),
    refresh: window.localStorage.getItem(REFRESH_KEY),
  };
}

export function setTokens(access: string, refresh: string) {
  window.localStorage.setItem(TOKEN_KEY, access);
  window.localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { access } = getTokens();
  if (access) {
    config.headers.set("Authorization", `Bearer ${access}`);
  }
  return config;
});

let isRefreshing = false;
let pendingQueue: Array<() => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    const { refresh } = getTokens();
    if (!refresh) {
      clearTokens();
      if (typeof window !== "undefined") window.location.href = "/login";
      return Promise.reject(error);
    }

    if (isRefreshing) {
      await new Promise<void>((resolve) => pendingQueue.push(resolve));
      return api(originalRequest);
    }

    originalRequest._retry = true;
    isRefreshing = true;
    try {
      const { data } = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refresh });
      setTokens(data.access_token, data.refresh_token);
      pendingQueue.forEach((resolve) => resolve());
      pendingQueue = [];
      return api(originalRequest);
    } catch (refreshError) {
      clearTokens();
      if (typeof window !== "undefined") window.location.href = "/login";
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);
