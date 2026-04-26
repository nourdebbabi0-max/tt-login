import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { firstLoginChangePasswordRequest } from "../../api/auth.api";
import AlertBox from "../../components/common/alertbox.jsx";

export default function FirstLoginPage() {
  const { user, logout } = useAuth();

  const [form, setForm] = useState({
    email: user?.email || "",
    mot_de_passe_actuel: "",
    nouveau_mot_de_passe: "",
    confirmation_nouveau_mot_de_passe: ""
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
    setLoading(true);

    try {
      const data = await firstLoginChangePasswordRequest(form);
      setMessage(data?.message || "Mot de passe changé avec succès.");

      setTimeout(() => {
        logout("/login");
      }, 1200);
    } catch (err) {
      const apiError = err?.data?.detail;
      if (typeof apiError === "string") {
        setError(apiError);
      } else {
        setError("Erreur lors du changement du mot de passe.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-center auth-page-bg">
      <div className="card auth-card">
        <div className="auth-header">
          <h1>Première connexion</h1>
          <p>Définissez votre mot de passe personnel.</p>
        </div>

        <AlertBox type="success" message={message} />
        <AlertBox type="error" message={error} />

        <form onSubmit={handleSubmit} className="form-stack">
          <div>
            <label htmlFor="email">Email</label>
            <input id="email" type="email" name="email" value={form.email} readOnly />
          </div>

          <div>
            <label htmlFor="mot_de_passe_actuel">Mot de passe actuel</label>
            <input
              id="mot_de_passe_actuel"
              type="password"
              name="mot_de_passe_actuel"
              value={form.mot_de_passe_actuel}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label htmlFor="nouveau_mot_de_passe">Nouveau mot de passe</label>
            <input
              id="nouveau_mot_de_passe"
              type="password"
              name="nouveau_mot_de_passe"
              value={form.nouveau_mot_de_passe}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <label htmlFor="confirmation_nouveau_mot_de_passe">Confirmation</label>
            <input
              id="confirmation_nouveau_mot_de_passe"
              type="password"
              name="confirmation_nouveau_mot_de_passe"
              value={form.confirmation_nouveau_mot_de_passe}
              onChange={handleChange}
              required
            />
          </div>

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Validation..." : "Valider"}
          </button>
        </form>
      </div>
    </div>
  );
}