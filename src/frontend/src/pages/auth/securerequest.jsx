import { useState } from "react";
import { Link } from "react-router-dom";
import { secureRecoveryRequest } from "../../api/auth.api";
import AlertBox from "../../components/common/AlertBox";
import { extractApiError } from "../../utils/errorMapper";

export default function SecureRecoveryRequestPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [codeDemande, setCodeDemande] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    setCodeDemande("");
    setLoading(true);

    try {
      const data = await secureRecoveryRequest({ email });
      setMessage(data?.message || "Demande sécurisée envoyée.");
      setCodeDemande(data?.code_demande || "");
      setEmail("");
    } catch (err) {
      setError(extractApiError(err?.data));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-center auth-page-bg">
      <div className="card auth-card">
        <div className="auth-header">
          <h1>Récupération sécurisée</h1>
          <p>Étape 1 : initier une demande sécurisée.</p>
        </div>

        <AlertBox type="success" message={message} />
        <AlertBox type="error" message={error} />

        {codeDemande ? (
          <div className="info-box">
            Code de demande : <strong>{codeDemande}</strong>
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="form-stack">
          <div>
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Envoi..." : "Démarrer la récupération sécurisée"}
          </button>
        </form>

        <div className="auth-links">
          <Link to="/login">Retour à la connexion</Link>
        </div>
      </div>
    </div>
  );
}