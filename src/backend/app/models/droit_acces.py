from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class DroitAcces(Base):
    __tablename__ = "droits_acces"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    nom_droit = Column(String(150), nullable=False)