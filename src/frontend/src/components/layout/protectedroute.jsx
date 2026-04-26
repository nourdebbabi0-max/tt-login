import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import LoadingScreen from "../common/loadingscreen";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, sessionChecked } = useAuth();

  if (!sessionChecked) {
    return <LoadingScreen message="Vérification de la session..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}