import axios, { AxiosError } from "axios";

import { getAccessToken, removeAccessToken } from "../auth/tokenStorage";
import { useAuthStore } from "../store/authStore";

const baseURL =
  process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

type AuthCallbacks = {
  onUnauthorized?: () => void;
};

let authCallbacks: AuthCallbacks = {};

export function configureApiAuthCallbacks(callbacks: AuthCallbacks) {
  authCallbacks = callbacks;
}

api.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      await removeAccessToken();
      useAuthStore.setState({ token: null, hydrated: true });
      authCallbacks.onUnauthorized?.();
    }
    return Promise.reject(error);
  },
);
