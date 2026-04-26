import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "utilisateurs"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    nom_complet = Column(String(150), nullable=False)

    mot_de_passe_hash = Column(Text, nullable=True)
    mot_de_passe_temporaire_hash = Column(Text, nullable=True)

    # 🔵 STATUTS
    est_actif = Column(Boolean, nullable=False, default=True)
    est_supprime = Column(Boolean, nullable=False, default=False)  # ⭐ AJOUT IMPORTANT
    premiere_connexion = Column(Boolean, nullable=False, default=True)
    compte_active = Column(Boolean, nullable=False, default=False)

    # 🔵 SECURITE
    nombre_echecs_connexion = Column(Integer, nullable=False, default=0)
    date_dernier_echec_connexion = Column(DateTime(timezone=True), nullable=True)
    blocage_jusqu_a = Column(DateTime(timezone=True), nullable=True)

    date_derniere_connexion = Column(DateTime(timezone=True), nullable=True)
    date_dernier_changement_mot_de_passe = Column(DateTime(timezone=True), nullable=True)

    # 🔵 META
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modification = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cree_par = Column(UUID(as_uuid=True), nullable=True)
    departement_id = Column(UUID(as_uuid=True), nullable=True)