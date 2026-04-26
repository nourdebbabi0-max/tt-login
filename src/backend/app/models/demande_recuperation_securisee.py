import uuid
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class DemandeRecuperationSecurisee(Base):
    __tablename__ = "demandes_recuperation_securisee"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), nullable=False)
    code_demande = Column(String(20), nullable=False)
    jeton_hash = Column(Text, nullable=False)
    expire_a = Column(DateTime(timezone=True), nullable=False)
    valide_a = Column(DateTime(timezone=True), nullable=True)
    utilise_a = Column(DateTime(timezone=True), nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)