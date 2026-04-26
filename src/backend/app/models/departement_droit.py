from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class DepartementDroit(Base):
    __tablename__ = "departement_droits"
    __table_args__ = {"schema": "app"}

    departement_id = Column(UUID(as_uuid=True), primary_key=True)
    droit_acces_id = Column(UUID(as_uuid=True), primary_key=True)