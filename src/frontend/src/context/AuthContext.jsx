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
      clearAuthStorage();
      setTokenState(null);
      setUserState(null);
      navigate("/session-expiree", { replace: true });
      return false;
    } finally {
      setSessionChecked(true);
    }
  }, [navigate]);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  const login = async ({ email, mot_de_passe }) => {
    setLoading(true);

    try {
      const data = await loginRequest({ email, mot_de_passe });

      /*
        Cas spécial : première connexion avec mot de passe temporaire.
        Ici on ne stocke pas access_token, parce que ce n'est pas encore
        une vraie session complète.
      */
      if (data.premiere_connexion) {
        clearAuthStorage();

        const firstLoginUser = {
          email: data.email || email,
          nom_complet: data.nom_complet || "",
          premiere_connexion: true
        };

        setTokenState(null);
        setUserState(firstLoginUser);

        navigate("/premiere-connexion", {
          replace: true,
          state: {
            email: data.email || email,
            mot_de_passe_actuel: mot_de_passe
          }
        });

        return data;
      }

      /*
        Cas normal : login complet avec vrai access_token.
      */
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

      navigate("/app", { replace: true });

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