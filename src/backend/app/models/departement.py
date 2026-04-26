import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class Departement(Base):
    __tablename__ = "departements"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_departement = Column(String(150), nullable=False, unique=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)