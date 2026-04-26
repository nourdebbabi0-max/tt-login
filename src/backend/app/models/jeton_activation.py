import uuid
from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class JetonActivation(Base):
    __tablename__ = "jetons_activation"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), nullable=False)
    jeton_hash = Column(Text, nullable=False)
    expire_a = Column(DateTime(timezone=True), nullable=False)
    utilise_a = Column(DateTime(timezone=True), nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)