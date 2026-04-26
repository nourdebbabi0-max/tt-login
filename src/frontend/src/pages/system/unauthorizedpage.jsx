import { Link } from "react-router-dom";

export default function UnauthorizedPage() {
  return (
    <div className="page-center auth-page-bg">
      <div className="card auth-card">
        <h1>Accès refusé</h1>
        <p>Vous n’avez pas les droits nécessaires pour accéder à cette page.</p>

        <div className="auth-links">
          <Link to="/app">Retour à l’accueil</Link>
        </div>
      </div>
    </div>
  );
}