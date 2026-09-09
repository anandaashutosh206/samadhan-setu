import { create } from "zustand";
import type { UserOut } from "@/types";
import { clearTokens, getTokens, setTokens } from "@/lib/api";

interface AuthState {
  user: UserOut | null;
  isHydrated: boolean;
  hydrate: () => void;
  login: (access: string, refresh: string, user: UserOut) => void;
  logout: () => void;
}

const USER_KEY = "samadhan_user";

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isHydrated: false,
  hydrate: () => {
    if (typeof window === "undefined") return;
    const { access } = getTokens();
    const raw = window.localStorage.getItem(USER_KEY);
    if (access && raw) {
      try {
        set({ user: JSON.parse(raw) as UserOut, isHydrated: true });
        return;
      } catch {
        // fall through to unauthenticated
      }
    }
    set({ user: null, isHydrated: true });
  },
  login: (access, refresh, user) => {
    setTokens(access, refresh);
    window.localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ user, isHydrated: true });
  },
  logout: () => {
    clearTokens();
    window.localStorage.removeItem(USER_KEY);
    set({ user: null, isHydrated: true });
  },
}));
