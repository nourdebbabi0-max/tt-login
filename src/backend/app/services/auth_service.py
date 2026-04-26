from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.user import User
from app.models.tentative_connexion import TentativeConnexion
from app.models.session_utilisateur import SessionUtilisateur
from app.models.jeton_activation import JetonActivation
from app.models.jeton_reinitialisation import JetonReinitialisation
from app.models.journal_audit import JournalAudit
from app.models.departement import Departement
import random
import uuid
from jose import jwt, JWTError

from app.models.historique_mot_de_passe import HistoriqueMotDePasse
from app.models.demande_recuperation_securisee import DemandeRecuperationSecurisee
from app.services.email_service import (
    envoyer_email_activation,
    envoyer_email_reinitialisation,
    envoyer_email_alerte_securite,
    envoyer_email_recuperation_securisee,
)

from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    generate_secure_token,
    hash_session_token,
    hash_generic_token,
)

from app.core.config import settings
from app.services.email_service import (
    envoyer_email_activation,
    envoyer_email_reinitialisation,
    envoyer_email_alerte_securite,
)
from app.services.password_policy_service import valider_nouveau_mot_de_passe


def _utcnow():
    return datetime.utcnow()


def _datetime_to_naive(dt_value):
    if not dt_value:
        return None

    if getattr(dt_value, "tzinfo", None):
        return dt_value.replace(tzinfo=None)

    return dt_value


def _est_admin(db: Session, user: User) -> bool:
    if not user or not user.departement_id:
        return False

    result = db.execute(
        text("""
            SELECT da.nom_droit
            FROM app.departement_droits dd
            JOIN app.droits_acces da
              ON dd.droit_acces_id = da.id
            WHERE dd.departement_id = :departement_id
        """),
        {"departement_id": user.departement_id},
    ).fetchall()

    droits = [row[0] for row in result] if result else []
    return "gerer_utilisateurs" in droits


def _calculer_duree_blocage(nombre_echecs: int, est_admin: bool) -> timedelta | None:
    if est_admin:
        if nombre_echecs <= 2:
            return None
        if nombre_echecs == 3:
            return timedelta(seconds=30)
        if nombre_echecs == 4:
            return timedelta(minutes=5)
        return timedelta(minutes=15)

    if nombre_echecs <= 3:
        return None
    if nombre_echecs == 4:
        return timedelta(seconds=30)
    if nombre_echecs == 5:
        return timedelta(seconds=60)
    if nombre_echecs == 6:
        return timedelta(minutes=5)
    return timedelta(minutes=15)


def _calculer_niveau_risque(
    nombre_echecs: int,
    est_admin: bool,
    raison_echec: str = None,
) -> str:
    if raison_echec == "ACCOUNT_BLOCKED":
        return "eleve"

    if est_admin:
        if nombre_echecs >= 4:
            return "eleve"
        if nombre_echecs >= 2:
            return "moyen"
        return "faible"

    if nombre_echecs >= 6:
        return "eleve"
    if nombre_echecs >= 4:
        return "moyen"
    return "faible"


def _journaliser_tentative(
    db: Session,
    utilisateur_id,
    email_saisi: str,
    succes: bool,
    raison_echec: str = None,
    niveau_risque: str = "faible",
):
    tentative = TentativeConnexion(
        utilisateur_id=utilisateur_id,
        email_saisi=email_saisi,
        succes=succes,
        raison_echec=raison_echec,
        niveau_risque=niveau_risque,
    )
    db.add(tentative)


def _journaliser_alerte_securite(db: Session, user: User, message: str):
    audit = JournalAudit(
        utilisateur_acteur_id=user.id if user else None,
        action_effectuee=message,
    )
    db.add(audit)


def _notifier_alerte_securite(user: User, type_alerte: str, details: str = ""):
    try:
        envoyer_email_alerte_securite(
            destinataire=user.email,
            nom_complet=user.nom_complet,
            type_alerte=type_alerte,
            details=details,
        )
    except Exception:
        pass


def _reset_echecs_connexion(user: User):
    user.nombre_echecs_connexion = 0
    user.date_dernier_echec_connexion = None
    user.blocage_jusqu_a = None


def _traiter_echec_connexion(
    db: Session,
    user: User,
    email: str,
    raison_echec: str = "EMAIL_OR_PASSWORD_INVALID",
):
    est_admin = _est_admin(db, user)

    nombre_echecs_actuel = user.nombre_echecs_connexion or 0
    user.nombre_echecs_connexion = nombre_echecs_actuel + 1
    user.date_dernier_echec_connexion = _utcnow()

    duree_blocage = _calculer_duree_blocage(
        nombre_echecs=user.nombre_echecs_connexion,
        est_admin=est_admin,
    )

    if duree_blocage:
        user.blocage_jusqu_a = _utcnow() + duree_blocage
    else:
        user.blocage_jusqu_a = None

    utilisateur_id = user.id if user else None

    niveau_risque = _calculer_niveau_risque(
        nombre_echecs=user.nombre_echecs_connexion,
        est_admin=est_admin,
        raison_echec=raison_echec,
    )

    if duree_blocage:
        _journaliser_alerte_securite(
            db=db,
            user=user,
            message=(
                f"SMART_LOCKOUT:{user.email}:"
                f"ECHECS={user.nombre_echecs_connexion}:"
                f"BLOCAGE_JUSQU_A={user.blocage_jusqu_a}"
            ),
        )

        _notifier_alerte_securite(
            user=user,
            type_alerte="Blocage temporaire du compte",
            details=(
                f"Votre compte a été temporairement restreint après "
                f"{user.nombre_echecs_connexion} tentative(s) de connexion non réussie(s)."
            ),
        )

        if est_admin:
            _journaliser_alerte_securite(
                db=db,
                user=user,
                message=f"ALERTE_SECURITE_ADMIN:{user.email}:BLOCAGE_RENFORCE",
            )

            _notifier_alerte_securite(
                user=user,
                type_alerte="Alerte sécurité renforcée administrateur",
                details=(
                    f"Un blocage renforcé a été appliqué à votre compte administrateur "
                    f"après plusieurs tentatives de connexion non réussies."
                ),
            )

    _journaliser_tentative(
        db=db,
        utilisateur_id=utilisateur_id,
        email_saisi=email,
        succes=False,
        raison_echec=raison_echec,
        niveau_risque=niveau_risque,
    )

    db.commit()


def authenticate_user(
    db: Session,
    email: str,
    mot_de_passe: str,
    adresse_ip: str = None,
    user_agent: str = None,
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        _journaliser_tentative(
            db=db,
            utilisateur_id=None,
            email_saisi=email,
            succes=False,
            raison_echec="EMAIL_OR_PASSWORD_INVALID",
            niveau_risque="faible",
        )
        db.commit()
        return None, "EMAIL_OR_PASSWORD_INVALID"

    blocage_jusqu_a = _datetime_to_naive(user.blocage_jusqu_a)
    maintenant = _utcnow()

    if blocage_jusqu_a and blocage_jusqu_a > maintenant:
        est_admin = _est_admin(db, user)
        niveau_risque = _calculer_niveau_risque(
            nombre_echecs=user.nombre_echecs_connexion or 0,
            est_admin=est_admin,
            raison_echec="ACCOUNT_BLOCKED",
        )

        _journaliser_tentative(
            db=db,
            utilisateur_id=user.id,
            email_saisi=email,
            succes=False,
            raison_echec="ACCOUNT_BLOCKED",
            niveau_risque=niveau_risque,
        )

        if est_admin:
            _journaliser_alerte_securite(
                db=db,
                user=user,
                message=f"TENTATIVE_PENDANT_BLOCAGE_ADMIN:{user.email}",
            )

        db.commit()
        return None, "ACCOUNT_BLOCKED"

    if not user.est_actif:
        _journaliser_tentative(
            db=db,
            utilisateur_id=user.id,
            email_saisi=email,
            succes=False,
            raison_echec="ACCOUNT_INACTIVE",
            niveau_risque="moyen",
        )
        db.commit()
        return None, "ACCOUNT_INACTIVE"

    if not user.compte_active:
        _journaliser_tentative(
            db=db,
            utilisateur_id=user.id,
            email_saisi=email,
            succes=False,
            raison_echec="ACCOUNT_NOT_ACTIVATED",
            niveau_risque="moyen",
        )
        db.commit()
        return None, "ACCOUNT_NOT_ACTIVATED"

    if not user.mot_de_passe_hash:
        _journaliser_tentative(
            db=db,
            utilisateur_id=user.id,
            email_saisi=email,
            succes=False,
            raison_echec="PASSWORD_NOT_SET",
            niveau_risque="moyen",
        )
        db.commit()
        return None, "PASSWORD_NOT_SET"

    try:
        mot_de_passe_valide = verify_password(mot_de_passe, user.mot_de_passe_hash)
    except Exception:
        _journaliser_tentative(
            db=db,
            utilisateur_id=user.id,
            email_saisi=email,
            succes=False,
            raison_echec="INVALID_STORED_PASSWORD_HASH",
            niveau_risque="eleve",
        )
        db.commit()
        return None, "INVALID_STORED_PASSWORD_HASH"

    if not mot_de_passe_valide:
        _traiter_echec_connexion(
            db=db,
            user=user,
            email=email,
            raison_echec="EMAIL_OR_PASSWORD_INVALID",
        )

        blocage_jusqu_a = _datetime_to_naive(user.blocage_jusqu_a)
        if blocage_jusqu_a and blocage_jusqu_a > _utcnow():
            return None, "ACCOUNT_BLOCKED"

        return None, "EMAIL_OR_PASSWORD_INVALID"

    _reset_echecs_connexion(user)
    user.date_derniere_connexion = _utcnow()

    _journaliser_tentative(
        db=db,
        utilisateur_id=user.id,
        email_saisi=email,
        succes=True,
        raison_echec=None,
        niveau_risque="faible",
    )

    audit = JournalAudit(
        utilisateur_acteur_id=user.id,
        action_effectuee=f"CONNEXION_REUSSIE:{user.email}",
    )
    db.add(audit)

    db.commit()
    db.refresh(user)

    if user.premiere_connexion:
        return user, "FIRST_LOGIN"

    return user, None


def build_first_login_response(db: Session, user: User):
    token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "premiere_connexion": True,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "email": user.email,
        "nom_complet": user.nom_complet,
        "est_actif": user.est_actif,
        "compte_active": user.compte_active,
        "premiere_connexion": user.premiere_connexion,
        "departement": None,
        "droits": [],
    }


def build_login_response(
    db: Session,
    user: User,
    adresse_ip: str = None,
    user_agent: str = None,
):
    departement_nom = None
    droits = []

    if user.departement_id:
        departement = (
            db.query(Departement).filter(Departement.id == user.departement_id).first()
        )
        if departement:
            departement_nom = departement.nom_departement

        result = db.execute(
            text("""
                SELECT da.nom_droit
                FROM app.departement_droits dd
                JOIN app.droits_acces da
                  ON dd.droit_acces_id = da.id
                WHERE dd.departement_id = :departement_id
            """),
            {"departement_id": user.departement_id},
        ).fetchall()

        droits = [row[0] for row in result] if result else []

    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "premiere_connexion": False,
        }
    )

    session_hash = hash_session_token(access_token)

    session = SessionUtilisateur(
        utilisateur_id=user.id,
        jeton_session_hash=session_hash,
        adresse_ip=adresse_ip,
        user_agent=user_agent,
        derniere_activite_a=_utcnow(),
        expire_a=_utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        revoque_a=None,
        raison_revocation=None,
    )
    db.add(session)

    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email,
        "nom_complet": user.nom_complet,
        "est_actif": user.est_actif,
        "compte_active": user.compte_active,
        "premiere_connexion": user.premiere_connexion,
        "departement": departement_nom,
        "droits": droits,
    }

def change_password_first_login(
    db: Session,
    email: str,
    mot_de_passe_actuel: str,
    nouveau_mot_de_passe: str,
    confirmation_nouveau_mot_de_passe: str,
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    if not user.est_actif:
        return None, "ACCOUNT_INACTIVE"

    if not user.premiere_connexion:
        return None, "NOT_FIRST_LOGIN"

    if nouveau_mot_de_passe != confirmation_nouveau_mot_de_passe:
        return None, "PASSWORD_CONFIRMATION_MISMATCH"

    if not user.mot_de_passe_hash:
        return None, "INVALID_STORED_PASSWORD_HASH"

    try:
        mot_de_passe_actuel_valide = verify_password(
            mot_de_passe_actuel,
            user.mot_de_passe_hash,
        )
    except Exception:
        return None, "INVALID_STORED_PASSWORD_HASH"

    if not mot_de_passe_actuel_valide:
        return None, "CURRENT_PASSWORD_INVALID"

    validation = valider_nouveau_mot_de_passe(
        mot_de_passe=nouveau_mot_de_passe,
        confirmation=confirmation_nouveau_mot_de_passe,
        email=user.email,
        nom_complet=user.nom_complet,
        departement="",
        ancien_mot_de_passe="",
    )

    if not validation["valide"]:
        return None, "PASSWORD_TOO_SHORT"

    if mot_de_passe_actuel == nouveau_mot_de_passe:
        return None, "NEW_PASSWORD_SAME_AS_OLD"

    user.mot_de_passe_hash = hash_password(nouveau_mot_de_passe)
    user.mot_de_passe_temporaire_hash = None
    user.premiere_connexion = False
    user.date_dernier_changement_mot_de_passe = _utcnow()

    audit = JournalAudit(
        utilisateur_acteur_id=user.id,
        action_effectuee=f"CHANGEMENT_MOT_DE_PASSE_PREMIERE_CONNEXION:{user.email}",
    )
    db.add(audit)

    db.commit()
    db.refresh(user)

    return user, None


def generer_lien_activation_premiere_connexion(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    if not user.est_actif:
        return None, "ACCOUNT_INACTIVE"

    if not user.premiere_connexion:
        return None, "NOT_FIRST_LOGIN"

    token_brut = generate_secure_token()
    token_hash = hash_generic_token(token_brut)
    token = token_brut

    jeton = JetonActivation(
        utilisateur_id=user.id,
        jeton_hash=token_hash,
        expire_a=_utcnow() + timedelta(minutes=15),
        utilise_a=None,
    )
    db.add(jeton)
    db.commit()

    activation_link = f"{settings.FRONTEND_ACTIVATION_URL}?token={token}"

    envoyer_email_activation(
        destinataire=user.email,
        nom_complet=user.nom_complet,
        activation_link=activation_link,
    )

    return {
        "message": "Lien d'activation envoyé avec succès",
        "email": user.email,
        "activation_link": activation_link,
    }, None


def valider_jeton_activation(db: Session, token: str):
    token_hash = hash_generic_token(token)

    jeton = db.query(JetonActivation).filter(
        JetonActivation.jeton_hash == token_hash
    ).first()

    if not jeton:
        return None, "TOKEN_NOT_FOUND"

    if jeton.utilise_a is not None:
        return None, "TOKEN_ALREADY_USED"

    expire_a = _datetime_to_naive(jeton.expire_a)
    if expire_a and expire_a < _utcnow():
        return None, "TOKEN_EXPIRED"

    user = db.query(User).filter(User.id == jeton.utilisateur_id).first()

    if not user:
        return None, "USER_NOT_FOUND"

    return {
        "message": "Jeton valide",
        "email": user.email,
        "nom_complet": user.nom_complet,
        "token_valide": True,
    }, None


def finaliser_activation_compte(db: Session, token: str, nouveau_mdp: str):
    token_hash = hash_generic_token(token)

    jeton = db.query(JetonActivation).filter(
        JetonActivation.jeton_hash == token_hash
    ).first()

    if not jeton:
        return None, "TOKEN_NOT_FOUND"

    if jeton.utilise_a is not None:
        return None, "TOKEN_ALREADY_USED"

    expire_a = _datetime_to_naive(jeton.expire_a)
    if expire_a and expire_a < _utcnow():
        return None, "TOKEN_EXPIRED"

    user = db.query(User).filter(User.id == jeton.utilisateur_id).first()

    if not user:
        return None, "USER_NOT_FOUND"

    validation = valider_nouveau_mot_de_passe(
        mot_de_passe=nouveau_mdp,
        confirmation=nouveau_mdp,
        email=user.email,
        nom_complet=user.nom_complet,
        departement="",
        ancien_mot_de_passe="",
    )

    if not validation["valide"]:
        return None, {
            "code": "PASSWORD_POLICY_ERROR",
            "erreurs": validation["erreurs"],
        }

    user.mot_de_passe_hash = hash_password(nouveau_mdp)
    user.compte_active = True
    user.premiere_connexion = False
    user.mot_de_passe_temporaire_hash = None
    user.date_dernier_changement_mot_de_passe = _utcnow()

    jeton.utilise_a = _utcnow()

    audit = JournalAudit(
        utilisateur_acteur_id=user.id,
        action_effectuee=f"ACTIVATION_COMPTE:{user.email}",
    )
    db.add(audit)

    db.commit()

    return {
        "message": "Compte activé avec succès",
        "email": user.email,
        "compte_active": user.compte_active,
        "premiere_connexion": user.premiere_connexion,
    }, None


def demander_reinitialisation_mot_de_passe(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    message_generique = {
        "message": "Si un compte existe avec cette adresse, un email de réinitialisation a été envoyé."
    }

    if not user:
        return message_generique, None

    if not user.est_actif:
        return message_generique, None

    anciens_jetons = db.query(JetonReinitialisation).filter(
        JetonReinitialisation.utilisateur_id == user.id,
        JetonReinitialisation.utilise_a.is_(None),
    ).all()

    for ancien in anciens_jetons:
        ancien.utilise_a = _utcnow()

    token_brut = generate_secure_token()
    token_hash = hash_generic_token(token_brut)
    token = token_brut

    jeton = JetonReinitialisation(
        utilisateur_id=user.id,
        jeton_hash=token_hash,
        expire_a=_utcnow()
        + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        utilise_a=None,
    )
    db.add(jeton)

    reset_link = (
        f"{settings.FRONTEND_ACTIVATION_URL.replace('activate-account', 'reset-password')}"
        f"?token={token}"
    )

    audit = JournalAudit(
        utilisateur_acteur_id=user.id,
        action_effectuee=f"DEMANDE_REINITIALISATION_MOT_DE_PASSE:{user.email}",
    )
    db.add(audit)

    db.commit()

    envoyer_email_reinitialisation(
        destinataire=user.email,
        nom_complet=user.nom_complet,
        reset_link=reset_link,
    )

    return message_generique, None


def valider_jeton_reinitialisation(db: Session, token: str):
    token_hash = hash_generic_token(token)

    jeton = db.query(JetonReinitialisation).filter(
        JetonReinitialisation.jeton_hash == token_hash
    ).first()

    if not jeton:
        return None, "TOKEN_NOT_FOUND"

    if jeton.utilise_a is not None:
        return None, "TOKEN_ALREADY_USED"

    expire_a = _datetime_to_naive(jeton.expire_a)
    if expire_a and expire_a < _utcnow():
        audit = JournalAudit(
            utilisateur_acteur_id=jeton.utilisateur_id,
            action_effectuee=f"TOKEN_REINITIALISATION_EXPIRE:{jeton.utilisateur_id}",
        )
        db.add(audit)
        db.commit()
        return None, "TOKEN_EXPIRED"

    user = db.query(User).filter(User.id == jeton.utilisateur_id).first()

    if not user:
        return None, "USER_NOT_FOUND"

    if not user.est_actif:
        return None, "ACCOUNT_INACTIVE"

    audit = JournalAudit(
        utilisateur_acteur_id=user.id,
        action_effectuee=f"TOKEN_REINITIALISATION_VALIDE:{user.email}",
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Jeton de réinitialisation valide",
        "email": user.email,
        "nom_complet": user.nom_complet,
        "token_valide": True,
    }, None


def reinitialiser_mot_de_passe(db: Session, token: str, nouveau_mdp: str):
    token_hash = hash_generic_token(token)

    jeton = db.query(JetonReinitialisation).filter(
        JetonReinitialisation.jeton_hash == token_hash
    ).first()

    if not jeton:
        _journaliser_audit(db, None, "RESET_PASSWORD_TOKEN_NOT_FOUND")
        db.commit()
        return None, "TOKEN_NOT_FOUND"

    if jeton.utilise_a is not None:
        _journaliser_audit(db, jeton.utilisateur_id, f"RESET_PASSWORD_TOKEN_ALREADY_USED:{jeton.utilisateur_id}")
        db.commit()
        return None, "TOKEN_ALREADY_USED"

    expire_a = _datetime_to_naive(jeton.expire_a)
    if expire_a and expire_a < _utcnow():
        _journaliser_audit(db, jeton.utilisateur_id, f"RESET_PASSWORD_TOKEN_EXPIRED:{jeton.utilisateur_id}")
        db.commit()
        return None, "TOKEN_EXPIRED"

    user = db.query(User).filter(User.id == jeton.utilisateur_id).first()

    if not user:
        _journaliser_audit(db, jeton.utilisateur_id, f"RESET_PASSWORD_USER_NOT_FOUND:{jeton.utilisateur_id}")
        db.commit()
        return None, "USER_NOT_FOUND"

    if not user.est_actif:
        _journaliser_audit(db, user.id, f"RESET_PASSWORD_ACCOUNT_INACTIVE:{user.email}")
        db.commit()
        return None, "ACCOUNT_INACTIVE"

    departement_nom = ""
    if user.departement_id:
        departement = db.query(Departement).filter(Departement.id == user.departement_id).first()
        if departement:
            departement_nom = departement.nom_departement

    validation = valider_nouveau_mot_de_passe(
        mot_de_passe=nouveau_mdp,
        confirmation=nouveau_mdp,
        email=user.email,
        nom_complet=user.nom_complet,
        departement=departement_nom,
        ancien_mot_de_passe="",
    )

    if not validation["valide"]:
        _journaliser_audit(db, user.id, f"RESET_PASSWORD_POLICY_REJECTED:{user.email}")
        db.commit()
        return None, {
            "code": "PASSWORD_POLICY_ERROR",
            "erreurs": validation["erreurs"],
        }

    if _mot_de_passe_deja_utilise_recemment(db, user, nouveau_mdp):
        _journaliser_audit(db, user.id, f"RESET_PASSWORD_REUSE_REJECTED:{user.email}")
        db.commit()
        return None, {
            "code": "PASSWORD_REUSE_FORBIDDEN",
            "erreurs": ["Ce mot de passe a déjà été utilisé récemment."],
        }

    if user.mot_de_passe_hash:
        _enregistrer_historique_mot_de_passe(db, user, user.mot_de_passe_hash)

    user.mot_de_passe_hash = hash_password(nouveau_mdp)
    user.mot_de_passe_temporaire_hash = None
    user.date_dernier_changement_mot_de_passe = _utcnow()

    _reset_echecs_connexion(user)

    jeton.utilise_a = _utcnow()

    autres_jetons = db.query(JetonReinitialisation).filter(
        JetonReinitialisation.utilisateur_id == user.id,
        JetonReinitialisation.utilise_a.is_(None),
        JetonReinitialisation.id != jeton.id
    ).all()

    for autre in autres_jetons:
        autre.utilise_a = _utcnow()

    sessions_actives = db.query(SessionUtilisateur).filter(
        SessionUtilisateur.utilisateur_id == user.id,
        SessionUtilisateur.revoque_a.is_(None)
    ).all()

    now_value = _utcnow()
    for session in sessions_actives:
        session.revoque_a = now_value
        session.raison_revocation = "PASSWORD_RESET"

    _journaliser_audit(db, user.id, f"REINITIALISATION_MOT_DE_PASSE:{user.email}")
    _journaliser_audit(db, user.id, f"REVOCATION_SESSIONS_APRES_RESET:{user.email}:NB={len(sessions_actives)}")

    db.commit()

    return {
        "message": "Mot de passe réinitialisé avec succès",
        "email": user.email,
    }, None


def _generer_code_demande() -> str:
    return f"{random.randint(100000, 999999)}"


def _journaliser_audit(db: Session, utilisateur_id, action: str):
    audit = JournalAudit(
        utilisateur_acteur_id=utilisateur_id,
        action_effectuee=action,
    )
    db.add(audit)


def _enregistrer_historique_mot_de_passe(db: Session, user: User, mot_de_passe_hash: str):
    historique = HistoriqueMotDePasse(
        utilisateur_id=user.id,
        mot_de_passe_hash=mot_de_passe_hash,
    )
    db.add(historique)


def _mot_de_passe_deja_utilise_recemment(db: Session, user: User, nouveau_mdp: str, limite: int = 5) -> bool:
    historiques = db.query(HistoriqueMotDePasse).filter(
        HistoriqueMotDePasse.utilisateur_id == user.id
    ).order_by(HistoriqueMotDePasse.date_creation.desc()).limit(limite).all()

    for item in historiques:
        try:
            if verify_password(nouveau_mdp, item.mot_de_passe_hash):
                return True
        except Exception:
            continue

    if user.mot_de_passe_hash:
        try:
            if verify_password(nouveau_mdp, user.mot_de_passe_hash):
                return True
        except Exception:
            pass

    return False


def demander_recuperation_securisee(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    code_demande = _generer_code_demande()
    message_generique = {
        "message": "Si ce compte existe, un message de poursuite a été envoyé.",
        "code_demande": code_demande,
    }

    if not user or not user.est_actif:
        return message_generique, None

    anciens = db.query(DemandeRecuperationSecurisee).filter(
        DemandeRecuperationSecurisee.utilisateur_id == user.id,
        DemandeRecuperationSecurisee.utilise_a.is_(None)
    ).all()

    for item in anciens:
        item.utilise_a = _utcnow()

    token_brut = generate_secure_token()
    token_hash = hash_generic_token(token_brut)
    token = token_brut

    demande = DemandeRecuperationSecurisee(
        utilisateur_id=user.id,
        code_demande=code_demande,
        jeton_hash=token_hash,
        expire_a=_utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(demande)

    recovery_link = f"{settings.FRONTEND_ACTIVATION_URL.replace('activate-account', 'secure-recovery')}?token={token}"

    _journaliser_audit(db, user.id, f"RECUPERATION_SECURISÉE_DEMANDEE:{user.email}")
    db.commit()

    envoyer_email_recuperation_securisee(
        destinataire=user.email,
        nom_complet=user.nom_complet,
        recovery_link=recovery_link,
        code_demande=code_demande,
    )

    return message_generique, None


def valider_recuperation_securisee(db: Session, token: str, code_demande: str):
    token_hash = hash_generic_token(token)

    demande = db.query(DemandeRecuperationSecurisee).filter(
        DemandeRecuperationSecurisee.jeton_hash == token_hash
    ).first()

    if not demande:
        _journaliser_audit(db, None, "RECUPERATION_SECURISÉE_TOKEN_NOT_FOUND")
        db.commit()
        return None, "TOKEN_NOT_FOUND"

    if demande.utilise_a is not None:
        _journaliser_audit(db, demande.utilisateur_id, f"RECUPERATION_SECURISÉE_TOKEN_ALREADY_USED:{demande.utilisateur_id}")
        db.commit()
        return None, "TOKEN_ALREADY_USED"

    expire_a = _datetime_to_naive(demande.expire_a)
    if expire_a and expire_a < _utcnow():
        _journaliser_audit(db, demande.utilisateur_id, f"RECUPERATION_SECURISÉE_TOKEN_EXPIRED:{demande.utilisateur_id}")
        db.commit()
        return None, "TOKEN_EXPIRED"

    if demande.code_demande != code_demande:
        _journaliser_audit(db, demande.utilisateur_id, f"RECUPERATION_SECURISÉE_CODE_INVALID:{demande.utilisateur_id}")
        db.commit()
        return None, "INVALID_REQUEST_CODE"

    user = db.query(User).filter(User.id == demande.utilisateur_id).first()

    if not user:
        _journaliser_audit(db, demande.utilisateur_id, f"RECUPERATION_SECURISÉE_USER_NOT_FOUND:{demande.utilisateur_id}")
        db.commit()
        return None, "USER_NOT_FOUND"

    if not user.est_actif:
        _journaliser_audit(db, user.id, f"RECUPERATION_SECURISÉE_ACCOUNT_INACTIVE:{user.email}")
        db.commit()
        return None, "ACCOUNT_INACTIVE"

    demande.valide_a = _utcnow()
    _journaliser_audit(db, user.id, f"RECUPERATION_SECURISÉE_VALIDEE:{user.email}")
    db.commit()

    return {
        "message": "Validation complémentaire réussie",
        "email": user.email,
        "nom_complet": user.nom_complet,
        "validation_ok": True,
    }, None


def reinitialiser_mot_de_passe_via_recuperation_securisee(
    db: Session,
    token: str,
    code_demande: str,
    nouveau_mdp: str,
):
    token_hash = hash_generic_token(token)

    demande = db.query(DemandeRecuperationSecurisee).filter(
        DemandeRecuperationSecurisee.jeton_hash == token_hash
    ).first()

    if not demande:
        _journaliser_audit(db, None, "RECUP_RESET_TOKEN_NOT_FOUND")
        db.commit()
        return None, "TOKEN_NOT_FOUND"

    if demande.utilise_a is not None:
        _journaliser_audit(db, demande.utilisateur_id, f"RECUP_RESET_TOKEN_ALREADY_USED:{demande.utilisateur_id}")
        db.commit()
        return None, "TOKEN_ALREADY_USED"

    expire_a = _datetime_to_naive(demande.expire_a)
    if expire_a and expire_a < _utcnow():
        _journaliser_audit(db, demande.utilisateur_id, f"RECUP_RESET_TOKEN_EXPIRED:{demande.utilisateur_id}")
        db.commit()
        return None, "TOKEN_EXPIRED"

    if demande.code_demande != code_demande:
        _journaliser_audit(db, demande.utilisateur_id, f"RECUP_RESET_CODE_INVALID:{demande.utilisateur_id}")
        db.commit()
        return None, "INVALID_REQUEST_CODE"

    if demande.valide_a is None:
        _journaliser_audit(db, demande.utilisateur_id, f"RECUP_RESET_NOT_PREVALIDATED:{demande.utilisateur_id}")
        db.commit()
        return None, "RECOVERY_NOT_VALIDATED"

    user = db.query(User).filter(User.id == demande.utilisateur_id).first()

    if not user:
        _journaliser_audit(db, demande.utilisateur_id, f"RECUP_RESET_USER_NOT_FOUND:{demande.utilisateur_id}")
        db.commit()
        return None, "USER_NOT_FOUND"

    if not user.est_actif:
        _journaliser_audit(db, user.id, f"RECUP_RESET_ACCOUNT_INACTIVE:{user.email}")
        db.commit()
        return None, "ACCOUNT_INACTIVE"

    departement_nom = ""
    if user.departement_id:
        departement = db.query(Departement).filter(Departement.id == user.departement_id).first()
        if departement:
            departement_nom = departement.nom_departement

    validation = valider_nouveau_mot_de_passe(
        mot_de_passe=nouveau_mdp,
        confirmation=nouveau_mdp,
        email=user.email,
        nom_complet=user.nom_complet,
        departement=departement_nom,
        ancien_mot_de_passe="",
    )

    if not validation["valide"]:
        _journaliser_audit(db, user.id, f"RECUP_RESET_POLICY_REJECTED:{user.email}")
        db.commit()
        return None, {
            "code": "PASSWORD_POLICY_ERROR",
            "erreurs": validation["erreurs"],
        }

    if _mot_de_passe_deja_utilise_recemment(db, user, nouveau_mdp):
        _journaliser_audit(db, user.id, f"RECUP_RESET_REUSE_REJECTED:{user.email}")
        db.commit()
        return None, {
            "code": "PASSWORD_REUSE_FORBIDDEN",
            "erreurs": ["Ce mot de passe a déjà été utilisé récemment."],
        }

    if user.mot_de_passe_hash:
        _enregistrer_historique_mot_de_passe(db, user, user.mot_de_passe_hash)

    user.mot_de_passe_hash = hash_password(nouveau_mdp)
    user.mot_de_passe_temporaire_hash = None
    user.date_dernier_changement_mot_de_passe = _utcnow()

    _reset_echecs_connexion(user)
    demande.utilise_a = _utcnow()

    sessions_actives = db.query(SessionUtilisateur).filter(
        SessionUtilisateur.utilisateur_id == user.id,
        SessionUtilisateur.revoque_a.is_(None)
    ).all()

    now_value = _utcnow()
    for session in sessions_actives:
        session.revoque_a = now_value
        session.raison_revocation = "SECURE_PASSWORD_RECOVERY"

    _journaliser_audit(db, user.id, f"RECUP_RESET_SUCCESS:{user.email}")
    _journaliser_audit(db, user.id, f"REVOCATION_SESSIONS_APRES_RECUP_RESET:{user.email}:NB={len(sessions_actives)}")

    db.commit()

    return {
        "message": "Mot de passe réinitialisé avec succès",
        "email": user.email,
    }, None

def _hash_access_token(token: str) -> str:
    return hash_session_token(token)


def verifier_session_backend(db: Session, access_token: str):
    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None, "INVALID_TOKEN"

    user_id = payload.get("user_id")
    email = payload.get("sub")

    if not user_id or not email:
        return None, "INVALID_TOKEN"

    session_hash = _hash_access_token(access_token)

    session = db.query(SessionUtilisateur).filter(
        SessionUtilisateur.jeton_session_hash == session_hash
    ).first()

    if not session:
        return None, "SESSION_NOT_FOUND"

    if session.revoque_a is not None:
        return None, "SESSION_REVOKED"

    maintenant = _utcnow()

    expire_a = _datetime_to_naive(session.expire_a)
    if expire_a and expire_a < maintenant:
        session.revoque_a = maintenant
        session.raison_revocation = "SESSION_EXPIRED"
        _journaliser_audit(db, session.utilisateur_id, f"SESSION_EXPIRED:{email}")
        db.commit()
        return None, "SESSION_EXPIRED"

    derniere_activite = _datetime_to_naive(session.derniere_activite_a) or _datetime_to_naive(session.date_creation)
    if derniere_activite and (maintenant - derniere_activite) > timedelta(minutes=settings.SESSION_INACTIVITY_EXPIRE_MINUTES):
        session.revoque_a = maintenant
        session.raison_revocation = "SESSION_INACTIVITY_TIMEOUT"
        _journaliser_audit(db, session.utilisateur_id, f"SESSION_INACTIVITY_TIMEOUT:{email}")
        db.commit()
        return None, "SESSION_INACTIVITY_TIMEOUT"

    session.derniere_activite_a = maintenant
    db.commit()

    user = db.query(User).filter(User.id == session.utilisateur_id).first()
    if not user:
        return None, "USER_NOT_FOUND"

    return user, None