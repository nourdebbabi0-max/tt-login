import uuid
from sqlalchemy import Column, DateTime, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class TentativeConnexion(Base):
    __tablename__ = "tentatives_connexion"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), nullable=True)
    email_saisi = Column(String, nullable=False)
    succes = Column(Boolean, nullable=False)
    raison_echec = Column(String(150), nullable=True)
    niveau_risque = Column(String(30), default="faible")
    date_tentative = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)