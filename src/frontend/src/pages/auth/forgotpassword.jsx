import { useState } from "react";
import { Link } from "react-router-dom";
import { forgotPasswordRequest } from "../../api/auth.api";
import AlertBox from "../../components/common/AlertBox";
import { extractApiError } from "../../utils/errorMapper";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    setLoading(true);

    try {
      const data = await forgotPasswordRequest({ email });
      setMessage(data?.message || "Demande envoyée avec succès.");
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
          <h1>Mot de passe oublié</h1>
          <p>Saisissez votre adresse email pour demander une réinitialisation.</p>
        </div>

        <AlertBox type="success" message={message} />
        <AlertBox type="error" message={error} />

        <form onSubmit={handleSubmit} className="form-stack">
          <div>
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="nom@tunisietelecom.tn"
              required
            />
          </div>

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Envoi..." : "Envoyer la demande"}
          </button>
        </form>

        <div className="auth-links">
          <Link to="/login">Retour à la connexion</Link>
        </div>
      </div>
    </div>
  );
}