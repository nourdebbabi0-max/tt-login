from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str


class Token(BaseModel):
    access_token: str
    token_type: str
    email: EmailStr
    nom_complet: str
    est_actif: bool
    compte_active: bool
    premiere_connexion: bool
    departement: Optional[str] = None
    droits: List[str] = []


class FirstLoginPasswordChange(BaseModel):
    email: EmailStr
    mot_de_passe_actuel: str
    nouveau_mot_de_passe: str
    confirmation_nouveau_mot_de_passe: str


class UserCreate(BaseModel):
    email: EmailStr
    nom_complet: str
    departement_id: str
    cree_par: Optional[str] = None


class UserCreateResponse(BaseModel):
    message: str
    email: EmailStr
    nom_complet: str
    departement_id: str
    mot_de_passe_temporaire: str
    premiere_connexion: bool
    compte_active: bool


class UserAdminItem(BaseModel):
    id: str
    email: EmailStr
    nom_complet: str
    est_actif: bool
    compte_active: bool
    premiere_connexion: bool
    departement: Optional[str] = None
    droits: List[str] = []

    departement_id: Optional[str] = None
    cree_par: Optional[str] = None

    nombre_echecs_connexion: int
    date_dernier_echec_connexion: Optional[str] = None
    blocage_jusqu_a: Optional[str] = None
    date_derniere_connexion: Optional[str] = None
    date_dernier_changement_mot_de_passe: Optional[str] = None
    date_creation: Optional[str] = None
    date_modification: Optional[str] = None

    a_mot_de_passe_temporaire: bool


class UserStatusUpdate(BaseModel):
    est_actif: bool
    acteur_id: Optional[str] = None


class UserStatusUpdateResponse(BaseModel):
    message: str
    user_id: str
    email: EmailStr
    est_actif: bool


class UserDeleteResponse(BaseModel):
    message: str
    user_id: str
    email: EmailStr
    est_actif: bool


class DepartementItem(BaseModel):
    id: str
    nom_departement: str
    date_creation: Optional[str] = None


class DepartementCreate(BaseModel):
    nom_departement: str


class DepartementCreateResponse(BaseModel):
    message: str
    id: str
    nom_departement: str


class ActivationLinkRequest(BaseModel):
    email: EmailStr


class ActivationLinkResponse(BaseModel):
    message: str
    email: EmailStr
    activation_link: str


class ActivationTokenValidateRequest(BaseModel):
    token: str


class ActivationTokenValidateResponse(BaseModel):
    message: str
    email: EmailStr
    nom_complet: str
    token_valide: bool


class ActivationSetPasswordRequest(BaseModel):
    token: str
    nouveau_mot_de_passe: str
    confirmation_mot_de_passe: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetRequestResponse(BaseModel):
    message: str


class PasswordResetTokenValidateRequest(BaseModel):
    token: str


class PasswordResetTokenValidateResponse(BaseModel):
    message: str
    email: EmailStr
    nom_complet: str
    token_valide: bool


class PasswordResetConfirmRequest(BaseModel):
    token: str
    nouveau_mot_de_passe: str
    confirmation_mot_de_passe: str


class PasswordResetConfirmResponse(BaseModel):
    message: str
    email: EmailStr

class PasswordRecoverySecureRequest(BaseModel):
    email: EmailStr


class PasswordRecoverySecureRequestResponse(BaseModel):
    message: str
    code_demande: str


class PasswordRecoverySecureValidateRequest(BaseModel):
    token: str
    code_demande: str


class PasswordRecoverySecureValidateResponse(BaseModel):
    message: str
    email: EmailStr
    nom_complet: str
    validation_ok: bool


class PasswordRecoverySecureResetRequest(BaseModel):
    token: str
    code_demande: str
    nouveau_mot_de_passe: str
    confirmation_mot_de_passe: str


class PasswordRecoverySecureResetResponse(BaseModel):
    message: str
    email: EmailStr
