import uuid
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class JournalAudit(Base):
    __tablename__ = "journal_audit"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_acteur_id = Column(UUID(as_uuid=True), nullable=True)
    action_effectuee = Column(String(150), nullable=False)
    date_action = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)