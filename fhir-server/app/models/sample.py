from sqlalchemy import (
    Column,
    String,
    Date,
    Boolean,
    ForeignKey,
    Integer,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import FHIRBase as Base
from app.models.enum import GenderType


class PatientModel(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    active = Column(Boolean, nullable=True)
    gender = Column(Enum(GenderType, name="gender_type"), nullable=True)
    birth_date = Column(Date, nullable=True)
    deceased_boolean = Column(Boolean, nullable=True)
    deceased_DateTime = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    identifiers = relationship(
        "PatientIdentifier", back_populates="patient", cascade="all, delete-orphan"
    )


class PatientIdentifier(Base):
    __tablename__ = "patient_identifier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

    patient = relationship("PatientModel", back_populates="identifiers")
