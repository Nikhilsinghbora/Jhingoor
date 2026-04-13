import { create } from "zustand";

import { removeAccessToken, setAccessToken } from "../auth/tokenStorage";

type AuthState = {
  token: string | null;
  hydrated: boolean;
  setSession: (token: string | null) => Promise<void>;
  hydrateFromStorage: (token: string | null) => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  hydrated: false,
  setSession: async (token) => {
    if (token) await setAccessToken(token);
    else await removeAccessToken();
    set({ token, hydrated: true });
  },
  hydrateFromStorage: (token) => set({ token, hydrated: true }),
}));
