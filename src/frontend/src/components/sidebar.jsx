import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { getMenuByDepartment } from "../utils/menuConfig";
import logoTT from "../assets/logo-tt.png";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const menuItems = getMenuByDepartment(user?.departement);

  return (
    <aside className="sidebar">
      <div>
        <div className="sidebar-brand">
          <div className="sidebar-logo-image-wrap">
            <img src={logoTT} alt="Tunisie Telecom" className="sidebar-logo-image" />
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
  );
}