import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AlertBox from "../../components/common/alertbox.jsx";
import { useAuth } from "../../hooks/useAuth";
import { extractApiError } from "../../utils/errorMapper";
import logoTT from "../../assets/logo-tt.png";

const cardsData = [
  {
    id: 1,
    title: "Plateforme sécurisée",
    text: "Accès centralisé aux services internes avec authentification renforcée et contrôle des accès."
  },
  {
    id: 2,
    title: "Gestion des utilisateurs",
    text: "Création, activation et administration des comptes collaborateurs par département."
  },
  {
    id: 3,
    title: "Tableaux de bord",
    text: "Consultez les données métiers, indicateurs clés et services essentiels au quotidien."
  }
];

function IconMail() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
    </svg>
  );
}

function IconLock() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );
}

function IconEye() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function IconEyeOff() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-10-7-10-7a18.06 18.06 0 0 1 5.06-5.94" />
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 10 7 10 7a18.2 18.2 0 0 1-2.16 3.19" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  );
}

export default function LoginPage() {
  const { login, loading } = useAuth();

  const [form, setForm] = useState({
    email: "",
    mot_de_passe: ""
  });

  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showLoginPanel, setShowLoginPanel] = useState(false);
  const [countdown, setCountdown] = useState(3);
  const [activeCard, setActiveCard] = useState(0);

  useEffect(() => {
    const splitTimer = setTimeout(() => {
      setShowLoginPanel(true);
    }, 3000);

    const countdownTimer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(countdownTimer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    const cardTimer = setInterval(() => {
      setActiveCard((prev) => (prev + 1) % cardsData.length);
    }, 1800);

    return () => {
      clearTimeout(splitTimer);
      clearInterval(countdownTimer);
      clearInterval(cardTimer);
    };
  }, []);

  function handleChange(e) {
    setError("");
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      await login(form);
    } catch (err) {
      setError(extractApiError(err?.data));
    }
  }

  return (
    <div className="page">
      <div className={`progress-bar ${showLoginPanel ? "progress-bar-done" : "progress-bar-running"}`} />

      <div className="page-bg page-bg-1" />
      <div className="page-bg page-bg-2" />
      <div className="page-bg page-bg-3" />

      <div className="top-notice">
        <div className="top-notice-left">
          <span className="top-notice-bell">🔔</span>
          <span>Plateforme interne Tunisie Telecom</span>
        </div>
        <div className="top-notice-right">
          Accès sécurisé aux services métier
        </div>
      </div>

      <div className={`layout ${showLoginPanel ? "layout-split" : ""}`}>
        <section className="welcome-panel">
          <div className="logo-wrap">
            <img src={logoTT} alt="Tunisie Telecom" className="logo" />
          </div>

          <div className="welcome-tag">WELCOME BACK</div>

          <h1 className="welcome-title">
            Votre espace interne
            <br />
            Tunisie Telecom
          </h1>

          <p className="welcome-desc">
            Accédez à toutes les informations, services et outils essentiels pour vous accompagner au quotidien.
          </p>

          <div className="accent-line" />

          <div className="carousel-shell">
            <div className="cards-track" style={{ transform: `translateX(-${activeCard * 25}%)` }}>
              {cardsData.concat(cardsData).map((card, index) => (
                <div
                  key={`${card.id}-${index}`}
                  className={`mini-card ${index === activeCard ? "mini-card-active" : ""}`}
                >
                  <h3>{card.title}</h3>
                  <p>{card.text}</p>
                </div>
              ))}
            </div>
          </div>

          {!showLoginPanel && (
            <div className="countdown-hint">
              Ouverture de l’espace de connexion dans{" "}
              <span className="countdown-num">{countdown}</span>s
            </div>
          )}
        </section>

        <section className={`login-panel ${showLoginPanel ? "login-panel-visible" : ""}`}>
          <div className="login-card">
            <h2 className="login-title">Connexion</h2>
            <p className="login-subtitle">Plateforme interne Tunisie Telecom</p>

            <AlertBox type="error" message={error} />

            <form onSubmit={handleSubmit}>
              <label className="field-label" htmlFor="email">
                Email
              </label>

              <div className="input-wrap">
                <span className="input-icon">
                  <IconMail />
                </span>

                <input
                  id="email"
                  type="email"
                  name="email"
                  placeholder="nom@tunisietelecom.tn"
                  value={form.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <label className="field-label" htmlFor="mot_de_passe">
                Mot de passe
              </label>

              <div className="input-wrap">
                <span className="input-icon">
                  <IconLock />
                </span>

                <input
                  id="mot_de_passe"
                  type={showPassword ? "text" : "password"}
                  name="mot_de_passe"
                  placeholder="Votre mot de passe"
                  value={form.mot_de_passe}
                  onChange={handleChange}
                  required
                />

                <button
                  type="button"
                  className="pwd-toggle"
                  onClick={() => setShowPassword((prev) => !prev)}
                >
                  {showPassword ? <IconEyeOff /> : <IconEye />}
                </button>
              </div>

              <button className="login-btn" type="submit" disabled={loading}>
                <span>{loading ? "Connexion..." : "Se connecter"}</span>
                <span className="btn-arrow">→</span>
              </button>
            </form>

            <div className="secure-text">Accès sécurisé</div>

            <div className="auth-links">
              <Link to="/mot-de-passe-oublie">Mot de passe oublié</Link>
              <Link to="/recuperation-securisee/request">Récupération sécurisée</Link>
            </div>

            <div className="secure-text">Connexion sécurisée</div>
          </div>
        </section>
      </div>
    </div>
  );
}