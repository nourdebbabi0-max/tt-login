import uuid
from sqlalchemy import Column, DateTime, Text, String
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
from app.core.database import Base


class SessionUtilisateur(Base):
    __tablename__ = "sessions_utilisateur"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), nullable=False)
    jeton_session_hash = Column(Text, nullable=False)
    adresse_ip = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    derniere_activite_a = Column(DateTime(timezone=True), nullable=True)
    expire_a = Column(DateTime(timezone=True), nullable=False)
    revoque_a = Column(DateTime(timezone=True), nullable=True)
    raison_revocation = Column(String(150), nullable=True)