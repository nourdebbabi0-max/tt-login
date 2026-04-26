import { useAuth } from "../hooks/useAuth";
import { Link } from "react-router-dom";

export default function HomePage() {
  const { user } = useAuth();

  const isAdmin = user?.departement === "Administration";

  return (
    <div className="content-grid">
      <section className="card dashboard-card">
        <h2>Accueil</h2>
        <p>
          Bienvenue <strong>{user?.nom_complet}</strong>.
        </p>
        <p>Email : {user?.email}</p>
        <p>Département : {user?.departement || "Non défini"}</p>
      </section>

      {isAdmin ? (
        <section className="admin-shortcuts-grid">
          <Link to="/app/admin/utilisateurs" className="admin-shortcut-card">
            <h3>Gérer les utilisateurs</h3>
            <p>Consulter, filtrer, rechercher et administrer les comptes.</p>
          </Link>

          <Link to="/app/commercial/avances" className="admin-shortcut-card">
            <h3>Suivi des avances</h3>
            <p>Accéder au module de suivi des avances.</p>
          </Link>

          <Link to="/app/commercial/remboursement" className="admin-shortcut-card">
            <h3>Suivi des remboursements</h3>
            <p>Accéder au module de remboursement.</p>
          </Link>

          <Link to="/app/commercial/service" className="admin-shortcut-card">
            <h3>Évolution des services</h3>
            <p>Consulter les indicateurs liés aux services.</p>
          </Link>

          <Link to="/app/commercial/bad-debts" className="admin-shortcut-card">
            <h3>Suivi des bad debts</h3>
            <p>Visualiser les créances et dossiers sensibles.</p>
          </Link>

          <Link to="/app/commercial/parc-sos-data" className="admin-shortcut-card">
            <h3>Parc SOS et DATA</h3>
            <p>Suivre l’évolution du parc SOS et DATA.</p>
          </Link>

          <Link to="/app/analyse/elt" className="admin-shortcut-card">
            <h3>ELT</h3>
            <p>Suivre les traitements ELT.</p>
          </Link>

          <Link to="/app/analyse/rapports-finaux" className="admin-shortcut-card">
            <h3>Rapports finaux</h3>
            <p>Accéder aux rapports consolidés.</p>
          </Link>
        </section>
      ) : null}
    </div>
  );
}