from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.reports import router as reports_router


from app.core.database import get_db
from app.models.user import User
from app.models.departement import Departement
from app.models.droit_acces import DroitAcces

from datetime import datetime

from app.schemas.main import (
    UserLogin,
    Token,
    FirstLoginPasswordChange,
    UserCreate,
    UserCreateResponse,
    UserAdminItem,
    UserStatusUpdate,
    UserStatusUpdateResponse,
    UserDeleteResponse,
    ActivationLinkRequest,
    ActivationLinkResponse,
    ActivationTokenValidateRequest,
    ActivationTokenValidateResponse,
    ActivationSetPasswordRequest,
    DepartementItem,
    DepartementCreate,
    DepartementCreateResponse,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    PasswordResetTokenValidateRequest,
    PasswordResetTokenValidateResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    PasswordRecoverySecureRequest,
    PasswordRecoverySecureRequestResponse,
    PasswordRecoverySecureValidateRequest,
    PasswordRecoverySecureValidateResponse,
    PasswordRecoverySecureResetRequest,
    PasswordRecoverySecureResetResponse,
)

from app.services.admin_service import (
    create_user_by_admin,
    list_users_with_rights,
    update_user_status_by_admin,
    delete_user_by_admin,
    list_departements,
    create_departement_by_admin,
)

from app.services.auth_service import (
    authenticate_user,
    build_login_response,
    build_first_login_response,
    change_password_first_login,
    generer_lien_activation_premiere_connexion,
    valider_jeton_activation,
    finaliser_activation_compte,
    demander_reinitialisation_mot_de_passe,
    valider_jeton_reinitialisation,
    reinitialiser_mot_de_passe,
    demander_recuperation_securisee,
    valider_recuperation_securisee,
    reinitialiser_mot_de_passe_via_recuperation_securisee,
    verifier_session_backend,
)


app = FastAPI(title="TT Internal Platform API")

security = HTTPBearer()


def get_current_user_active_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    user, error = verifier_session_backend(db, token)

    if error == "INVALID_TOKEN":
        raise HTTPException(status_code=401, detail="Token invalide")

    if error == "SESSION_NOT_FOUND":
        raise HTTPException(status_code=401, detail="Session introuvable")

    if error == "SESSION_REVOKED":
        raise HTTPException(status_code=401, detail="Session révoquée")

    if error == "SESSION_EXPIRED":
        raise HTTPException(
            status_code=401,
            detail="Votre session a expiré. Veuillez vous reconnecter."
        )

    if error == "SESSION_INACTIVITY_TIMEOUT":
        raise HTTPException(
            status_code=401,
            detail="Votre session a expiré pour cause d’inactivité. Veuillez vous ré-authentifier."
        )

    if error == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    return user

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "http://localhost:5178",
        "http://127.0.0.1:5178",
        "http://localhost:5179",
        "http://127.0.0.1:5179",
        "http://localhost:5180",
        "http://127.0.0.1:5180",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(reports_router)

@app.get("/")
def root():
    return {"message": "Backend OK"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/session/check")
def session_check(current_user=Depends(get_current_user_active_session)):
    return {
        "message": "Session active",
        "email": current_user.email,
        "nom_complet": current_user.nom_complet,
    }


@app.get("/api/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT current_database(), current_schema(), now()")
    ).fetchone()

    return {
        "status": "success",
        "message": "Connexion DB réussie",
        "database": result[0],
        "schema": result[1],
        "server_time": str(result[2]),
    }


@app.get("/api/test-users-orm")
def test_users_orm(db: Session = Depends(get_db)):
    users = db.query(User).limit(10).all()
    return {
        "status": "success",
        "count": len(users),
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "nom_complet": user.nom_complet,
            }
            for user in users
        ],
    }


@app.get("/api/test-departements-orm")
def test_departements_orm(db: Session = Depends(get_db)):
    departements = db.query(Departement).limit(10).all()
    return {
        "status": "success",
        "count": len(departements),
        "departements": [
            {
                "id": str(dep.id),
                "nom_departement": dep.nom_departement,
                "date_creation": str(dep.date_creation) if dep.date_creation else None,
            }
            for dep in departements
        ],
    }


@app.get("/api/test-droits-orm")
def test_droits_orm(db: Session = Depends(get_db)):
    droits = db.query(DroitAcces).limit(20).all()
    return {
        "status": "success",
        "count": len(droits),
        "droits": [
            {
                "id": str(droit.id),
                "nom_droit": droit.nom_droit,
            }
            for droit in droits
        ],
    }


@app.get("/api/test-departement-droits-detail")
def test_departement_droits_detail(db: Session = Depends(get_db)):
    result = db.execute(
        text(
            """
            SELECT
                d.nom_departement,
                da.nom_droit
            FROM app.departement_droits dd
            JOIN app.departements d
                ON dd.departement_id = d.id
            JOIN app.droits_acces da
                ON dd.droit_acces_id = da.id
            ORDER BY d.nom_departement, da.nom_droit
            """
        )
    ).fetchall()

    return {
        "status": "success",
        "count": len(result),
        "data": [
            {
                "nom_departement": row[0],
                "nom_droit": row[1],
            }
            for row in result
        ],
    }


@app.post("/api/login", response_model=Token)
def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        adresse_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        user, error_code = authenticate_user(
            db=db,
            email=user_data.email,
            mot_de_passe=user_data.mot_de_passe,
            adresse_ip=adresse_ip,
            user_agent=user_agent,
        )

        if error_code == "ACCOUNT_BLOCKED":
            user_db = db.query(User).filter(User.email == user_data.email).first()

            retry_after_seconds = None
            if user_db and user_db.blocage_jusqu_a:
                blocage_jusqu_a = user_db.blocage_jusqu_a
                if getattr(blocage_jusqu_a, "tzinfo", None):
                    blocage_jusqu_a = blocage_jusqu_a.replace(tzinfo=None)

                now_value = datetime.utcnow()
                delta = (blocage_jusqu_a - now_value).total_seconds()
                retry_after_seconds = max(0, int(delta)) if delta > 0 else 0

            raise HTTPException(
                status_code=423,
                detail={
                    "detail": "Accès temporairement restreint. Veuillez réessayer plus tard.",
                    "code": "ACCOUNT_TEMP_BLOCKED",
                    "retry_after_seconds": retry_after_seconds,
                },
            )

        if error_code in [
            "EMAIL_OR_PASSWORD_INVALID",
            "PASSWORD_NOT_SET",
            "INVALID_STORED_PASSWORD_HASH",
        ]:
            raise HTTPException(
                status_code=401,
                detail={
                    "detail": "Identifiants invalides ou accès temporairement restreint.",
                    "code": "AUTH_FAILED",
                },
            )

        if error_code == "ACCOUNT_INACTIVE":
            raise HTTPException(
                status_code=403,
                detail={
                    "detail": "Compte désactivé.",
                    "code": "ACCOUNT_INACTIVE",
                },
            )

        if error_code == "ACCOUNT_NOT_ACTIVATED":
            raise HTTPException(
                status_code=403,
                detail={
                    "detail": "Compte non activé.",
                    "code": "ACCOUNT_NOT_ACTIVATED",
                },
            )

        if error_code == "FIRST_LOGIN":
            return build_first_login_response(db=db, user=user)

        return build_login_response(
            db=db,
            user=user,
            adresse_ip=adresse_ip,
            user_agent=user_agent,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "detail": "Erreur interne lors de l'authentification.",
                "code": "LOGIN_INTERNAL_ERROR",
                "debug": str(e),
            },
        )


@app.post("/api/change-password-first-login")
def change_password_first_login_endpoint(
    data: FirstLoginPasswordChange,
    db: Session = Depends(get_db),
):
    user, error_code = change_password_first_login(
        db=db,
        email=data.email,
        mot_de_passe_actuel=data.mot_de_passe_actuel,
        nouveau_mot_de_passe=data.nouveau_mot_de_passe,
        confirmation_nouveau_mot_de_passe=data.confirmation_nouveau_mot_de_passe,
    )

    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if error_code == "ACCOUNT_INACTIVE":
        raise HTTPException(status_code=403, detail="Compte désactivé")

    if error_code == "NOT_FIRST_LOGIN":
        raise HTTPException(status_code=400, detail="Pas première connexion")

    if error_code == "PASSWORD_CONFIRMATION_MISMATCH":
        raise HTTPException(status_code=400, detail="Confirmation incorrecte")

    if error_code == "PASSWORD_TOO_SHORT":
        raise HTTPException(status_code=400, detail="Mot de passe trop court")

    if error_code == "CURRENT_PASSWORD_INVALID":
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")

    if error_code == "NEW_PASSWORD_SAME_AS_OLD":
        raise HTTPException(status_code=400, detail="Mot de passe identique")

    if error_code == "INVALID_STORED_PASSWORD_HASH":
        raise HTTPException(status_code=500, detail="Erreur hash")

    return {
        "message": "Mot de passe changé avec succès",
        "email": user.email,
        "premiere_connexion": user.premiere_connexion,
        "compte_active": user.compte_active,
    }


@app.post("/api/admin/create-user", response_model=UserCreateResponse)
def admin_create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    result, error_code = create_user_by_admin(
        db=db,
        email=data.email,
        nom_complet=data.nom_complet,
        departement_id=data.departement_id,
        cree_par=data.cree_par,
    )

    if error_code == "EMAIL_ALREADY_EXISTS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà",
        )

    if error_code == "DEPARTMENT_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Département introuvable",
        )

    return result


@app.get("/api/admin/users", response_model=list[UserAdminItem])
def admin_list_users(db: Session = Depends(get_db)):
    users, error_code = list_users_with_rights(db=db)

    if error_code:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des utilisateurs",
        )

    return users


@app.patch("/api/admin/users/{user_id}/status", response_model=UserStatusUpdateResponse)
def admin_update_user_status(
    user_id: str,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
):
    result, error_code = update_user_status_by_admin(
        db=db,
        user_id=user_id,
        est_actif=data.est_actif,
        acteur_id=data.acteur_id,
    )

    if error_code == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable",
        )

    return result


@app.delete("/api/admin/users/{user_id}", response_model=UserDeleteResponse)
def admin_delete_user(
    user_id: str,
    acteur_id: str = None,
    db: Session = Depends(get_db)
):
    result, error_code = delete_user_by_admin(
        db=db,
        user_id=user_id,
        acteur_id=acteur_id
    )

    if error_code == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )

    return result


@app.get("/api/departements", response_model=list[DepartementItem])
def get_departements(db: Session = Depends(get_db)):
    result, error_code = list_departements(db=db)

    if error_code == "DEPARTEMENTS_FETCH_ERROR":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur technique lors de la récupération des départements. Vérifie la table app.departements et le schéma PostgreSQL."
        )

    if error_code:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des départements"
        )

    return result


@app.post("/api/departements", response_model=DepartementCreateResponse)
def create_departement(
    data: DepartementCreate,
    db: Session = Depends(get_db)
):
    result, error_code = create_departement_by_admin(
        db=db,
        nom_departement=data.nom_departement
    )

    if error_code == "INVALID_DEPARTMENT_NAME":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom de département invalide"
        )

    if error_code == "DEPARTMENT_ALREADY_EXISTS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce département existe déjà"
        )

    if error_code == "DEPARTMENT_CREATE_ERROR":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur technique lors de la création du département"
        )

    return result


@app.post("/api/activation/request-link", response_model=ActivationLinkResponse)
def request_activation_link(
    data: ActivationLinkRequest,
    db: Session = Depends(get_db),
):
    try:
        result, error_code = generer_lien_activation_premiere_connexion(
            db=db,
            email=data.email,
        )

        if error_code == "USER_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable",
            )

        if error_code == "ACCOUNT_INACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé",
            )

        if error_code == "NOT_FIRST_LOGIN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet utilisateur n'est pas en première connexion",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ERREUR_REQUEST_LINK_DEBUG: {str(e)}",
        )


@app.post("/api/activation/validate-token", response_model=ActivationTokenValidateResponse)
def validate_activation_token(
    data: ActivationTokenValidateRequest,
    db: Session = Depends(get_db),
):
    try:
        result, error_code = valider_jeton_activation(
            db=db,
            token=data.token,
        )

        if error_code == "TOKEN_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jeton d'activation introuvable",
            )

        if error_code == "TOKEN_ALREADY_USED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jeton d'activation déjà utilisé",
            )

        if error_code == "TOKEN_EXPIRED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jeton d'activation expiré",
            )

        if error_code == "USER_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ERREUR_VALIDATE_TOKEN_DEBUG: {str(e)}",
        )


@app.post("/api/activation/set-password")
def set_password_after_activation(
    data: ActivationSetPasswordRequest,
    db: Session = Depends(get_db),
):
    if data.nouveau_mot_de_passe != data.confirmation_mot_de_passe:
        raise HTTPException(
            status_code=400,
            detail="Les mots de passe ne correspondent pas",
        )

    result, error = finaliser_activation_compte(
        db=db,
        token=data.token,
        nouveau_mdp=data.nouveau_mot_de_passe,
    )

    if error == "TOKEN_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Jeton introuvable")

    if error == "TOKEN_ALREADY_USED":
        raise HTTPException(status_code=400, detail="Jeton déjà utilisé")

    if error == "TOKEN_EXPIRED":
        raise HTTPException(status_code=400, detail="Jeton expiré")

    if error == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if isinstance(error, dict) and error.get("code") == "PASSWORD_POLICY_ERROR":
        raise HTTPException(status_code=400, detail=error["erreurs"])

    return result


@app.post("/api/password-forgot/request", response_model=PasswordResetRequestResponse)
def password_forgot_request(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    result, _ = demander_reinitialisation_mot_de_passe(
        db=db,
        email=data.email,
    )
    return result


@app.post("/api/password-forgot/validate-token", response_model=PasswordResetTokenValidateResponse)
def password_forgot_validate_token(
    data: PasswordResetTokenValidateRequest,
    db: Session = Depends(get_db),
):
    result, error_code = valider_jeton_reinitialisation(
        db=db,
        token=data.token,
    )

    if error_code == "TOKEN_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Jeton introuvable")

    if error_code == "TOKEN_ALREADY_USED":
        raise HTTPException(status_code=400, detail="Jeton déjà utilisé")

    if error_code == "TOKEN_EXPIRED":
        raise HTTPException(status_code=400, detail="Jeton expiré")

    if error_code == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if error_code == "ACCOUNT_INACTIVE":
        raise HTTPException(status_code=403, detail="Compte désactivé")

    return result


@app.post("/api/password-forgot/reset", response_model=PasswordResetConfirmResponse)
def password_forgot_reset(
    data: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
):
    if data.nouveau_mot_de_passe != data.confirmation_mot_de_passe:
        raise HTTPException(
            status_code=400,
            detail="Les mots de passe ne correspondent pas",
        )

    result, error = reinitialiser_mot_de_passe(
        db=db,
        token=data.token,
        nouveau_mdp=data.nouveau_mot_de_passe,
    )

    if error == "TOKEN_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Jeton introuvable")

    if error == "TOKEN_ALREADY_USED":
        raise HTTPException(status_code=400, detail="Jeton déjà utilisé")

    if error == "TOKEN_EXPIRED":
        raise HTTPException(status_code=400, detail="Jeton expiré")

    if error == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if error == "ACCOUNT_INACTIVE":
        raise HTTPException(status_code=403, detail="Compte désactivé")

    if isinstance(error, dict) and error.get("code") == "PASSWORD_POLICY_ERROR":
        raise HTTPException(status_code=400, detail=error["erreurs"])

    if isinstance(error, dict) and error.get("code") == "PASSWORD_REUSE_FORBIDDEN":
        raise HTTPException(status_code=400, detail=error["erreurs"])

    return result


@app.post("/api/password-recovery/secure-request", response_model=PasswordRecoverySecureRequestResponse)
def password_recovery_secure_request(
    data: PasswordRecoverySecureRequest,
    db: Session = Depends(get_db),
):
    result, _ = demander_recuperation_securisee(
        db=db,
        email=data.email,
    )
    return result


@app.post("/api/password-recovery/secure-validate", response_model=PasswordRecoverySecureValidateResponse)
def password_recovery_secure_validate(
    data: PasswordRecoverySecureValidateRequest,
    db: Session = Depends(get_db),
):
    result, error = valider_recuperation_securisee(
        db=db,
        token=data.token,
        code_demande=data.code_demande,
    )

    if error == "TOKEN_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Jeton introuvable")
    if error == "TOKEN_ALREADY_USED":
        raise HTTPException(status_code=400, detail="Jeton déjà utilisé")
    if error == "TOKEN_EXPIRED":
        raise HTTPException(status_code=400, detail="Jeton expiré")
    if error == "INVALID_REQUEST_CODE":
        raise HTTPException(status_code=400, detail="Code de demande invalide")
    if error == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if error == "ACCOUNT_INACTIVE":
        raise HTTPException(status_code=403, detail="Compte désactivé")

    return result


@app.post("/api/password-recovery/secure-reset", response_model=PasswordRecoverySecureResetResponse)
def password_recovery_secure_reset(
    data: PasswordRecoverySecureResetRequest,
    db: Session = Depends(get_db),
):
    if data.nouveau_mot_de_passe != data.confirmation_mot_de_passe:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")

    result, error = reinitialiser_mot_de_passe_via_recuperation_securisee(
        db=db,
        token=data.token,
        code_demande=data.code_demande,
        nouveau_mdp=data.nouveau_mot_de_passe,
    )

    if error == "TOKEN_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Jeton introuvable")
    if error == "TOKEN_ALREADY_USED":
        raise HTTPException(status_code=400, detail="Jeton déjà utilisé")
    if error == "TOKEN_EXPIRED":
        raise HTTPException(status_code=400, detail="Jeton expiré")
    if error == "INVALID_REQUEST_CODE":
        raise HTTPException(status_code=400, detail="Code de demande invalide")
    if error == "RECOVERY_NOT_VALIDATED":
        raise HTTPException(status_code=400, detail="Validation complémentaire non effectuée")
    if error == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if error == "ACCOUNT_INACTIVE":
        raise HTTPException(status_code=403, detail="Compte désactivé")
    if isinstance(error, dict) and error.get("code") in ["PASSWORD_POLICY_ERROR", "PASSWORD_REUSE_FORBIDDEN"]:
        raise HTTPException(status_code=400, detail=error["erreurs"])

    return result