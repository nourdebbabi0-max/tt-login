import uuid
from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class HistoriqueMotDePasse(Base):
    __tablename__ = "historiques_mots_de_passe"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), nullable=False)
    mot_de_passe_hash = Column(Text, nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)