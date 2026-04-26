import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../hooks/useAuth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function AdminUsersPage() {
  const { token } = useAuth();

  const [activeTab, setActiveTab] = useState("liste");

  const [users, setUsers] = useState([]);
  const [departements, setDepartements] = useState([]);

  const [loading, setLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState("");
  const [createLoading, setCreateLoading] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [search, setSearch] = useState("");
  const [selectedDepartement, setSelectedDepartement] = useState("all");
  const [expandedUserId, setExpandedUserId] = useState("");

  const [createForm, setCreateForm] = useState({
    email: "",
    nom_complet: "",
    departement_id: ""
  });

  const [createdUserInfo, setCreatedUserInfo] = useState(null);

  useEffect(() => {
    fetchUsers();
    fetchDepartements();
  }, []);

  async function fetchUsers() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: token
          ? {
              Authorization: `Bearer ${token}`
            }
          : {}
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Erreur lors du chargement des utilisateurs.");
      }

      setUsers(data);
    } catch (err) {
      setError(err.message || "Erreur lors du chargement des utilisateurs.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchDepartements() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/departements`);
      const data = await response.json();

      if (!response.ok) return;
      setDepartements(data);
    } catch {
      // silencieux
    }
  }

  function handleCreateChange(e) {
    setCreateForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  }

  async function handleCreateUser(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setCreatedUserInfo(null);
    setCreateLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/create-user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          email: createForm.email,
          nom_complet: createForm.nom_complet,
          departement_id: createForm.departement_id
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Erreur lors de la création de l’utilisateur.");
      }

      setSuccess(`Utilisateur créé avec succès : ${data.nom_complet}`);
      setCreatedUserInfo(data);

      setCreateForm({
        email: "",
        nom_complet: "",
        departement_id: ""
      });

      await fetchUsers();
      setActiveTab("liste");
    } catch (err) {
      setError(err.message || "Erreur lors de la création de l’utilisateur.");
    } finally {
      setCreateLoading(false);
    }
  }

  async function handleToggleStatus(targetUser) {
    setError("");
    setSuccess("");
    setActionLoadingId(targetUser.id);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${targetUser.id}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {})
          },
          body: JSON.stringify({
            est_actif: !targetUser.est_actif
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Erreur lors de la mise à jour du statut.");
      }

      setSuccess(`Statut mis à jour pour ${targetUser.nom_complet}.`);
      await fetchUsers();
    } catch (err) {
      setError(err.message || "Erreur lors de la mise à jour du statut.");
    } finally {
      setActionLoadingId("");
    }
  }

  async function handleDeleteUser(targetUser) {
    const confirmed = window.confirm(
      `Voulez-vous vraiment supprimer logiquement ${targetUser.nom_complet} ?`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");
    setActionLoadingId(targetUser.id);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${targetUser.id}`,
        {
          method: "DELETE",
          headers: token
            ? {
                Authorization: `Bearer ${token}`
              }
            : {}
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Erreur lors de la suppression.");
      }

      setSuccess(`Utilisateur supprimé : ${targetUser.nom_complet}.`);
      await fetchUsers();
    } catch (err) {
      setError(err.message || "Erreur lors de la suppression.");
    } finally {
      setActionLoadingId("");
    }
  }

  const filteredUsers = useMemo(() => {
    return users.filter((item) => {
      const matchesSearch =
        item.nom_complet?.toLowerCase().includes(search.toLowerCase()) ||
        item.email?.toLowerCase().includes(search.toLowerCase());

      const matchesDepartement =
        selectedDepartement === "all" ||
        item.departement === selectedDepartement;

      return matchesSearch && matchesDepartement;
    });
  }, [users, search, selectedDepartement]);

  return (
    <div className="content-grid">
      <section className="card dashboard-card">
        <div className="admin-page-header">
          <div>
            <h2>Gestion des utilisateurs</h2>
            <p>
              Créer, consulter, filtrer, activer, désactiver et supprimer des utilisateurs.
            </p>
          </div>

          <div className="admin-tab-actions">
            <button
              className={`tab-switch-btn ${activeTab === "liste" ? "tab-switch-btn-active" : ""}`}
              onClick={() => setActiveTab("liste")}
            >
              Liste des utilisateurs
            </button>
            <button
              className={`tab-switch-btn ${activeTab === "creation" ? "tab-switch-btn-active" : ""}`}
              onClick={() => setActiveTab("creation")}
            >
              Créer un utilisateur
            </button>
          </div>
        </div>
      </section>

      {error ? <div className="alert-box alert-error">{error}</div> : null}
      {success ? <div className="alert-box alert-success">{success}</div> : null}

      {createdUserInfo ? (
        <section className="card dashboard-card temp-password-card">
          <h3>Utilisateur créé</h3>
          <p><strong>Nom :</strong> {createdUserInfo.nom_complet}</p>
          <p><strong>Email :</strong> {createdUserInfo.email}</p>
          <p><strong>Première connexion :</strong> {createdUserInfo.premiere_connexion ? "Oui" : "Non"}</p>
          <p><strong>Compte activé :</strong> {createdUserInfo.compte_active ? "Oui" : "Non"}</p>

          <div className="temp-password-box">
            <span>Mot de passe temporaire</span>
            <strong>{createdUserInfo.mot_de_passe_temporaire}</strong>
          </div>

          <p className="temp-password-help">
            Donne cet email et ce mot de passe temporaire au nouvel utilisateur.
            À sa première connexion, il devra le changer.
          </p>
        </section>
      ) : null}

      {activeTab === "creation" ? (
        <section className="card dashboard-card">
          <h3>Créer un utilisateur</h3>

          <form className="admin-create-form" onSubmit={handleCreateUser}>
            <div className="admin-form-group">
              <label>Nom complet</label>
              <input
                type="text"
                name="nom_complet"
                value={createForm.nom_complet}
                onChange={handleCreateChange}
                placeholder="Ex : Amira Ben Abd"
                required
              />
            </div>

            <div className="admin-form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={createForm.email}
                onChange={handleCreateChange}
                placeholder="exemple@tunisietelecom.tn"
                required
              />
            </div>

            <div className="admin-form-group">
              <label>Département</label>
              <select
                name="departement_id"
                value={createForm.departement_id}
                onChange={handleCreateChange}
                required
              >
                <option value="">Sélectionner un département</option>
                {departements.map((dep) => (
                  <option key={dep.id} value={dep.id}>
                    {dep.nom_departement}
                  </option>
                ))}
              </select>
            </div>

            <div className="admin-form-submit">
              <button className="primary-btn" type="submit" disabled={createLoading}>
                {createLoading ? "Création..." : "Créer l’utilisateur"}
              </button>
            </div>
          </form>
        </section>
      ) : null}

      {activeTab === "liste" ? (
        <>
          <section className="admin-toolbar">
            <div className="admin-toolbar-group">
              <label>Rechercher</label>
              <input
                type="text"
                placeholder="Nom ou email"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="admin-toolbar-group">
              <label>Filtrer par département</label>
              <select
                value={selectedDepartement}
                onChange={(e) => setSelectedDepartement(e.target.value)}
              >
                <option value="all">Tous les départements</option>
                {departements.map((dep) => (
                  <option key={dep.id} value={dep.nom_departement}>
                    {dep.nom_departement}
                  </option>
                ))}
              </select>
            </div>

            <div className="admin-toolbar-actions">
              <button className="primary-btn small-btn" onClick={fetchUsers}>
                {loading ? "Chargement..." : "Actualiser"}
              </button>
            </div>
          </section>

          <section className="card dashboard-card">
            <div className="admin-users-header">
              <h3>Liste des utilisateurs</h3>
              <span>{filteredUsers.length} utilisateur(s)</span>
            </div>

            <div className="admin-users-table-wrap">
              <table className="admin-users-table">
                <thead>
                  <tr>
                    <th>Nom</th>
                    <th>Email</th>
                    <th>Département</th>
                    <th>Statut</th>
                    <th>Compte</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="empty-cell">
                        Aucun utilisateur trouvé.
                      </td>
                    </tr>
                  ) : (
                    filteredUsers.map((item) => {
                      const expanded = expandedUserId === item.id;
                      const isBusy = actionLoadingId === item.id;

                      return (
                        <>
                          <tr key={item.id}>
                            <td>{item.nom_complet}</td>
                            <td>{item.email}</td>
                            <td>{item.departement || "Non défini"}</td>
                            <td>
                              <span className={`status-badge ${item.est_actif ? "status-active" : "status-inactive"}`}>
                                {item.est_actif ? "Actif" : "Inactif"}
                              </span>
                            </td>
                            <td>
                              <span className={`status-badge ${item.compte_active ? "status-active" : "status-pending"}`}>
                                {item.compte_active ? "Activé" : "En attente"}
                              </span>
                            </td>
                            <td>
                              <div className="table-action-group">
                                <button
                                  className="table-btn secondary"
                                  onClick={() => setExpandedUserId(expanded ? "" : item.id)}
                                >
                                  {expanded ? "Voir moins" : "Voir plus"}
                                </button>

                                <button
                                  className="table-btn primary"
                                  onClick={() => handleToggleStatus(item)}
                                  disabled={isBusy}
                                >
                                  {item.est_actif ? "Désactiver" : "Activer"}
                                </button>

                                <button
                                  className="table-btn danger"
                                  onClick={() => handleDeleteUser(item)}
                                  disabled={isBusy}
                                >
                                  Supprimer
                                </button>
                              </div>
                            </td>
                          </tr>

                          {expanded ? (
                            <tr key={`${item.id}-details`}>
                              <td colSpan="6">
                                <div className="user-details-panel">
                                  <div><strong>ID :</strong> {item.id}</div>
                                  <div><strong>Nom complet :</strong> {item.nom_complet}</div>
                                  <div><strong>Email :</strong> {item.email}</div>
                                  <div><strong>Département :</strong> {item.departement || "Non défini"}</div>
                                  <div><strong>Droits :</strong> {item.droits?.length ? item.droits.join(", ") : "Aucun droit"}</div>
                                  <div><strong>Première connexion :</strong> {item.premiere_connexion ? "Oui" : "Non"}</div>
                                  <div><strong>Date de création :</strong> {item.date_creation || "Non disponible"}</div>
                                  <div><strong>Dernière connexion :</strong> {item.date_derniere_connexion || "Non disponible"}</div>
                                  <div><strong>Échecs de connexion :</strong> {item.nombre_echecs_connexion ?? 0}</div>
                                </div>
                              </td>
                            </tr>
                          ) : null}
                        </>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}