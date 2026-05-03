import { Outlet, NavLink, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { useAuth } from "../../hooks/useAuth";
import { getMenuByDepartment } from "../../utils/menuconfig.js";
import logoTT from "../../assets/logo-tt.png";

function getPageTitle(pathname) {
  const map = {
    "/app": "Accueil",

    "/app/powerbi/home": "Home dashboard",
    "/app/powerbi/avances": "Suivi des avances",
    "/app/powerbi/avances-heure": "Suivi par heure ADV",
    "/app/powerbi/remboursement": "Suivi des remboursements",
    "/app/powerbi/remboursement-heure": "Suivi par heure REV",
    "/app/powerbi/service": "Suivi des services",
    "/app/powerbi/aide-decision": "Aide à la décision",

    "/app/commercial/parc-sos-data": "Parc SOS DATA",
    "/app/commercial/bad-debts": "Bad Debts",

    "/app/analyse/elt": "ELT",
    "/app/analyse/rapports-finaux": "Rapports finaux",

    "/app/admin/utilisateurs": "Gestion des utilisateurs"
  };

  return map[pathname] || "Dashboard";
}

export default function AppShell() {
  const { user, logout, checkSession } = useAuth();
  const location = useLocation();

  const menuItems = getMenuByDepartment(user?.departement);

  useEffect(() => {
    const interval = setInterval(() => {
      checkSession();
    }, 3 * 60 * 1000);

    return () => clearInterval(interval);
  }, [checkSession]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="sidebar-brand">
            <div className="sidebar-logo-image-wrap">
              <img
                src={logoTT}
                alt="Tunisie Telecom"
                className="sidebar-logo-image"
              />
            </div>

            <div>
              <h2>Plateforme TT</h2>
              <p>Interne & sécurisée</p>
            </div>
          </div>

          <div className="sidebar-user-box">
            <strong>{user?.nom_complet || "Utilisateur"}</strong>
            <span>{user?.email || ""}</span>
            <span>{user?.departement || "Département non défini"}</span>
          </div>

          <nav className="sidebar-nav">
            {menuItems.map((item) => (
              <NavLink key={item.path} to={item.path} className="sidebar-link">
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <button className="logout-btn" onClick={() => logout("/login")}>
          Se déconnecter
        </button>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div>
            <h1 className="topbar-title">{getPageTitle(location.pathname)}</h1>
            <p className="topbar-subtitle">
              Bienvenue, {user?.nom_complet || "Utilisateur"}
            </p>
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}