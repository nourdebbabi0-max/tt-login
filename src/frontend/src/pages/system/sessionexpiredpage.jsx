import { Link } from "react-router-dom";

export default function SessionExpiredPage() {
  return (
    <div className="page-center auth-page-bg">
      <div className="card auth-card">
        <h1>Session expirée</h1>
        <p>Votre session a expiré. Veuillez vous reconnecter.</p>

        <div className="auth-links">
          <Link to="/login">Retour à la connexion</Link>
        </div>
      </div>
    </div>
  );
}