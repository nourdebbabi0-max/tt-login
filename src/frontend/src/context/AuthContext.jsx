import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginRequest, checkSessionRequest } from "../api/auth.api";
import {
  clearAuthStorage,
  getToken,
  getUser,
  setToken,
  setUser
} from "../utils/storage";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const navigate = useNavigate();

  const [token, setTokenState] = useState(getToken());
  const [user, setUserState] = useState(getUser());
  const [loading, setLoading] = useState(false);
  const [sessionChecked, setSessionChecked] = useState(false);

  const logout = useCallback(
    (redirectTo = "/login") => {
      clearAuthStorage();
      setTokenState(null);
      setUserState(null);
      navigate(redirectTo, { replace: true });
    },
    [navigate]
  );

  const checkSession = useCallback(async () => {
    const existingToken = getToken();
    const existingUser = getUser();

    if (!existingToken || !existingUser) {
      setSessionChecked(true);
      return false;
    }

    try {
      await checkSessionRequest();
      setTokenState(existingToken);
      setUserState(existingUser);
      return true;
    } catch {
      logout("/session-expiree");
      return false;
    } finally {
      setSessionChecked(true);
    }
  }, [logout]);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  const login = async ({ email, mot_de_passe }) => {
    setLoading(true);

    try {
      const data = await loginRequest({ email, mot_de_passe });

      const connectedUser = {
        email: data.email,
        nom_complet: data.nom_complet,
        est_actif: data.est_actif,
        compte_active: data.compte_active,
        premiere_connexion: data.premiere_connexion,
        departement: data.departement,
        droits: data.droits || []
      };

      setToken(data.access_token);
      setUser(connectedUser);

      setTokenState(data.access_token);
      setUserState(connectedUser);

      if (data.premiere_connexion) {
        navigate("/premiere-connexion", { replace: true });
      } else {
        navigate("/app", { replace: true });
      }

      return data;
    } finally {
      setLoading(false);
    }
  };

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      sessionChecked,
      isAuthenticated: !!token,
      login,
      logout,
      checkSession
    }),
    [token, user, loading, sessionChecked, logout, checkSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}