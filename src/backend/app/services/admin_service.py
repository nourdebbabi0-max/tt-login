import secrets
import string
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.user import User
from app.models.departement import Departement
from app.models.journal_audit import JournalAudit
from app.core.security import hash_password

LONGUEUR_MDP_TEMPORAIRE = 12


def generer_mot_de_passe_temporaire(longueur: int = LONGUEUR_MDP_TEMPORAIRE) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%&*?"
    return "".join(secrets.choice(alphabet) for _ in range(longueur))


def create_user_by_admin(
    db: Session,
    email: str,
    nom_complet: str,
    departement_id: str,
    cree_par: str = None
):
    utilisateur_existant = (
        db.query(User)
        .filter(User.email == email, User.est_supprime.is_(False))
        .first()
    )
    if utilisateur_existant:
        return None, "EMAIL_ALREADY_EXISTS"

    departement = db.query(Departement).filter(Departement.id == departement_id).first()
    if not departement:
        return None, "DEPARTMENT_NOT_FOUND"

    mot_de_passe_temporaire = generer_mot_de_passe_temporaire()

    nouvel_utilisateur = User(
        email=email,
        nom_complet=nom_complet,
        departement_id=departement_id,
        mot_de_passe_hash=hash_password(mot_de_passe_temporaire),
        mot_de_passe_temporaire_hash=hash_password(mot_de_passe_temporaire),
        est_actif=True,
        est_supprime=False,
        premiere_connexion=True,
        compte_active=True,
        nombre_echecs_connexion=0,
        cree_par=cree_par
    )

    db.add(nouvel_utilisateur)
    db.flush()

    audit = JournalAudit(
        utilisateur_acteur_id=cree_par,
        action_effectuee=f"CREATION_UTILISATEUR:{email}"
    )
    db.add(audit)

    db.commit()
    db.refresh(nouvel_utilisateur)

    return {
        "message": "Utilisateur créé avec succès",
        "email": nouvel_utilisateur.email,
        "nom_complet": nouvel_utilisateur.nom_complet,
        "departement_id": str(nouvel_utilisateur.departement_id),
        "mot_de_passe_temporaire": mot_de_passe_temporaire,
        "premiere_connexion": nouvel_utilisateur.premiere_connexion,
        "compte_active": nouvel_utilisateur.compte_active
    }, None


def list_users_with_rights(db: Session):
    result = db.execute(
        text("""
            SELECT
                u.id,
                u.email,
                u.nom_complet,
                u.est_actif,
                u.compte_active,
                u.premiere_connexion,
                d.nom_departement,
                da.nom_droit,
                u.departement_id,
                u.cree_par,
                u.nombre_echecs_connexion,
                u.date_dernier_echec_connexion,
                u.blocage_jusqu_a,
                u.date_derniere_connexion,
                u.date_dernier_changement_mot_de_passe,
                u.date_creation,
                u.date_modification,
                CASE
                    WHEN u.mot_de_passe_temporaire_hash IS NOT NULL THEN TRUE
                    ELSE FALSE
                END AS a_mot_de_passe_temporaire
            FROM app.utilisateurs u
            LEFT JOIN app.departements d
                ON u.departement_id = d.id
            LEFT JOIN app.departement_droits dd
                ON d.id = dd.departement_id
            LEFT JOIN app.droits_acces da
                ON dd.droit_acces_id = da.id
            WHERE u.est_supprime = FALSE
            ORDER BY u.nom_complet, da.nom_droit
        """)
    ).fetchall()

    users_map = {}

    for row in result:
        user_id = str(row[0])

        if user_id not in users_map:
            users_map[user_id] = {
                "id": user_id,
                "email": row[1],
                "nom_complet": row[2],
                "est_actif": row[3],
                "compte_active": row[4],
                "premiere_connexion": row[5],
                "departement": row[6],
                "droits": [],
                "departement_id": str(row[8]) if row[8] else None,
                "cree_par": str(row[9]) if row[9] else None,
                "nombre_echecs_connexion": row[10],
                "date_dernier_echec_connexion": str(row[11]) if row[11] else None,
                "blocage_jusqu_a": str(row[12]) if row[12] else None,
                "date_derniere_connexion": str(row[13]) if row[13] else None,
                "date_dernier_changement_mot_de_passe": str(row[14]) if row[14] else None,
                "date_creation": str(row[15]) if row[15] else None,
                "date_modification": str(row[16]) if row[16] else None,
                "a_mot_de_passe_temporaire": row[17],
            }

        if row[7] and row[7] not in users_map[user_id]["droits"]:
            users_map[user_id]["droits"].append(row[7])

    return list(users_map.values()), None


def update_user_status_by_admin(
    db: Session,
    user_id: str,
    est_actif: bool,
    acteur_id: str = None
):
    user = (
        db.query(User)
        .filter(User.id == user_id, User.est_supprime.is_(False))
        .first()
    )

    if not user:
        return None, "USER_NOT_FOUND"

    user.est_actif = est_actif

    audit = JournalAudit(
        utilisateur_acteur_id=acteur_id,
        action_effectuee=f"MODIFICATION_STATUT_UTILISATEUR:{user.email}:{est_actif}"
    )
    db.add(audit)

    db.commit()
    db.refresh(user)

    return {
        "message": "Statut utilisateur mis à jour avec succès",
        "user_id": str(user.id),
        "email": user.email,
        "est_actif": user.est_actif
    }, None


def delete_user_by_admin(
    db: Session,
    user_id: str,
    acteur_id: str = None
):
    user = (
        db.query(User)
        .filter(User.id == user_id, User.est_supprime.is_(False))
        .first()
    )

    if not user:
        return None, "USER_NOT_FOUND"

    user.est_supprime = True

    audit = JournalAudit(
        utilisateur_acteur_id=acteur_id,
        action_effectuee=f"SUPPRESSION_LOGIQUE_UTILISATEUR:{user.email}"
    )
    db.add(audit)

    db.commit()
    db.refresh(user)

    return {
        "message": "Utilisateur supprimé avec succès",
        "user_id": str(user.id),
        "email": user.email,
        "est_actif": user.est_actif
    }, None


def list_departements(db: Session):
    try:
        departements = db.query(Departement).order_by(Departement.nom_departement.asc()).all()

        return [
            {
                "id": str(dep.id),
                "nom_departement": dep.nom_departement,
                "date_creation": str(dep.date_creation) if dep.date_creation else None
            }
            for dep in departements
        ], None

    except Exception as e:
        print("ERREUR list_departements :", str(e))
        return None, "DEPARTEMENTS_FETCH_ERROR"


def create_departement_by_admin(db: Session, nom_departement: str):
    try:
        nom_normalise = (nom_departement or "").strip()

        if not nom_normalise:
            return None, "INVALID_DEPARTMENT_NAME"

        existe = db.query(Departement).filter(
            Departement.nom_departement == nom_normalise
        ).first()

        if existe:
            return None, "DEPARTMENT_ALREADY_EXISTS"

        nouveau = Departement(
            nom_departement=nom_normalise
        )

        db.add(nouveau)
        db.commit()
        db.refresh(nouveau)

        return {
            "message": "Département créé avec succès",
            "id": str(nouveau.id),
            "nom_departement": nouveau.nom_departement
        }, None

    except Exception as e:
        print("ERREUR create_departement_by_admin :", str(e))
        return None, "DEPARTMENT_CREATE_ERROR"