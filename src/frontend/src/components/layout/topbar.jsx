import { useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

function getPageTitle(pathname) {
  const map = {
    "/app": "Accueil",
    "/app/commercial/dashboard-avance": "Dashboard avancé",
    "/app/commercial/remboursement": "Dashboard remboursement",
    "/app/commercial/service": "Service",
    "/app/commercial/parc-sos-data": "Parc SOS DATA",
    "/app/commercial/bad-debts": "Bad Debts",
    "/app/analyse/elt": "ELT",
    "/app/analyse/rapports-finaux": "Rapports finaux"
  };

  return map[pathname] || "Dashboard";
}

export default function Topbar() {
  const { user } = useAuth();
  const location = useLocation();

  return (
    <header className="topbar">
      <div>
        <h1 className="topbar-title">{getPageTitle(location.pathname)}</h1>
        <p className="topbar-subtitle">
          Bienvenue, {user?.nom_complet || "Utilisateur"}
        </p>
      </div>
    </header>
  );
}