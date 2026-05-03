import { useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

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