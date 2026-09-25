import React, { createContext, useContext, useEffect, useState } from "react";
import { AUTH_EXPIRED_EVENT, getMe, loginLocal } from "../lib/api.js";

const STORAGE_KEY = "joyeria-local-session";
const AuthContext = createContext(null);

function readStoredSession() {
  try {
    const session = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (!session?.accessToken || !session?.expiresAt || session.expiresAt <= Date.now()) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return session;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(readStoredSession);
  const [restoring, setRestoring] = useState(Boolean(session));

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setRestoring(false);
  };

  useEffect(() => {
    const handleExpired = () => logout();
    window.addEventListener(AUTH_EXPIRED_EVENT, handleExpired);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleExpired);
  }, []);

  useEffect(() => {
    if (!session) {
      setRestoring(false);
      return undefined;
    }
    const controller = new AbortController();
    setRestoring(true);
    getMe(session.accessToken, controller.signal)
      .then((user) => {
        const refreshed = { ...session, user };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(refreshed));
        setSession(refreshed);
      })
      .catch((error) => {
        if (error.name !== "AbortError") logout();
      })
      .finally(() => setRestoring(false));
    return () => controller.abort();
  }, [session?.accessToken]);

  const login = async (email, password) => {
    const response = await loginLocal(email, password);
    const nextSession = {
      accessToken: response.access_token,
      expiresAt: Date.now() + response.expires_in * 1000,
      user: response.user
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
    setSession(nextSession);
  };

  return React.createElement(AuthContext.Provider, {
    value: {
      token: session?.accessToken || null,
      user: session?.user || null,
      restoring,
      login,
      logout
    }
  }, children);
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return context;
}
