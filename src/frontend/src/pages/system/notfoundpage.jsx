import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="page-center auth-page-bg">
      <div className="card auth-card">
        <h1>404</h1>
        <p>Page introuvable.</p>

        <div className="auth-links">
          <Link to="/login">Aller à la connexion</Link>
        </div>
      </div>
    </div>
  );
}