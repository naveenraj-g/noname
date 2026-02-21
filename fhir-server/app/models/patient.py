from sqlalchemy import Column, String, Date, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import FHIRBase as Base


class PatientModel(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    active = Column(Boolean, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    deceased_boolean = Column(Boolean, nullable=True)
    # deceased_datetime could be added if needed

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    identifiers = relationship(
        "PatientIdentifier", back_populates="patient", cascade="all, delete-orphan"
    )
    names = relationship(
        "PatientName", back_populates="patient", cascade="all, delete-orphan"
    )
    telecoms = relationship(
        "PatientTelecom", back_populates="patient", cascade="all, delete-orphan"
    )
    addresses = relationship(
        "PatientAddress", back_populates="patient", cascade="all, delete-orphan"
    )

    encounters = relationship(
        "EncounterModel", back_populates="patient", cascade="all, delete-orphan"
    )

    encounter_participations = relationship(
        "EncounterParticipant",
        back_populates="patient",
        foreign_keys="EncounterParticipant.patient_id",
    )


class PatientIdentifier(Base):
    __tablename__ = "patient_identifier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

    system = Column(String, nullable=True)
    value = Column(String, nullable=True)
    use = Column(String, nullable=True)

    patient = relationship("PatientModel", back_populates="identifiers")


class PatientName(Base):
    __tablename__ = "patient_name"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

    use = Column(String, nullable=True)
    family = Column(String, nullable=True)
    given = Column(
        String, nullable=True
    )  # Storing as comma-separated string for simplicity in SQL or use another table for given names. Here: simplified to string.
    text = Column(String, nullable=True)

    patient = relationship("PatientModel", back_populates="names")


class PatientTelecom(Base):
    __tablename__ = "patient_telecom"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

    system = Column(String, nullable=True)
    value = Column(String, nullable=True)
    use = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)

    patient = relationship("PatientModel", back_populates="telecoms")


class PatientAddress(Base):
    __tablename__ = "patient_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

    use = Column(String, nullable=True)
    type = Column(String, nullable=True)
    text = Column(String, nullable=True)
    line = Column(String, nullable=True)  # Comma separated for simplicity
    city = Column(String, nullable=True)
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)

    patient = relationship("PatientModel", back_populates="addresses")
