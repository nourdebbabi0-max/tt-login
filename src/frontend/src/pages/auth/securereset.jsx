import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { secureRecoveryResetRequest } from "../../api/auth.api";
import AlertBox from "../../components/common/AlertBox";
import { extractApiError } from "../../utils/errorMapper";

export default function SecureRecoveryResetPage() {
  const [searchParams] = useSearchParams();
  const token = useMemo(() => searchParams.get("token") || "", [searchParams]);

  const [form, setForm] = useState({
    code_demande: "",
    nouveau_mot_de_passe: "",
    confirmation_mot_de_passe: ""
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setError("");
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    if (!token) {
      setError("Token manquant dans l’URL.");
      return;
    }

    setLoading(true);

    try {
      const data = await secureRecoveryResetRequest({
        token,
        code_demande: form.code_demande,
        nouveau_mot_de_passe: form.nouveau_mot_de_passe,
        confirmation_mot_de_passe: form.confirmation_mot_de_passe
      });

      setMessage(data?.message || "Mot de passe réinitialisé avec succès.");
      setForm({
        code_demande: "",
        nouveau_mot_de_passe: "",
        confirmation_mot_de_passe: ""
      });
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
          <h1>Reset sécurisé</h1>
          <p>Étape 3 : saisissez votre code de demande et votre nouveau mot de passe.</p>
        </div>

        <AlertBox type="success" message={message} />
        <AlertBox type="error" message={error} />

        <form onSubmit={handleSubmit} className="form-stack">
          <div>
            <label>Code de demande</label>
            <input
              type="text"
              name="code_demande"
              value={form.code_demande}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label>Nouveau mot de passe</label>
            <input
              type="password"
              name="nouveau_mot_de_passe"
              value={form.nouveau_mot_de_passe}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label>Confirmation du mot de passe</label>
            <input
              type="password"
              name="confirmation_mot_de_passe"
              value={form.confirmation_mot_de_passe}
              onChange={handleChange}
              required
            />
          </div>

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Validation..." : "Valider le reset sécurisé"}
          </button>
        </form>

        <div className="auth-links">
          <Link to="/login">Retour à la connexion</Link>
        </div>
      </div>
    </div>
  );
}