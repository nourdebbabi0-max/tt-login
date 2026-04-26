import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { secureRecoveryValidateRequest } from "../../api/auth.api";
import AlertBox from "../../components/common/AlertBox";
import { extractApiError } from "../../utils/errorMapper";

export default function SecureRecoveryValidatePage() {
  const [searchParams] = useSearchParams();
  const token = useMemo(() => searchParams.get("token") || "", [searchParams]);

  const [code_demande, setCodeDemande] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    setResult(null);

    if (!token) {
      setError("Token manquant dans l’URL.");
      return;
    }

    setLoading(true);

    try {
      const data = await secureRecoveryValidateRequest({
        token,
        code_demande
      });

      setResult(data);
      setMessage(data?.message || "Validation réussie.");
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
          <h1>Validation sécurisée</h1>
          <p>Étape 2 : saisissez le code de demande reçu.</p>
        </div>

        <AlertBox type="success" message={message} />
        <AlertBox type="error" message={error} />

        <form onSubmit={handleSubmit} className="form-stack">
          <div>
            <label>Code de demande</label>
            <input
              type="text"
              value={code_demande}
              onChange={(e) => setCodeDemande(e.target.value)}
              required
            />
          </div>

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Validation..." : "Valider"}
          </button>
        </form>

        {result ? (
          <div className="info-box">
            <div><strong>Email :</strong> {result.email}</div>
            <div><strong>Nom :</strong> {result.nom_complet}</div>
          </div>
        ) : null}

        <div className="auth-links">
          <Link to="/login">Retour à la connexion</Link>
        </div>
      </div>
    </div>
  );
}