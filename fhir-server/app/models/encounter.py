from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import FHIRBase as Base
from .enum import ParticipantReferenceType


class EncounterModel(Base):
    __tablename__ = "encounter"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    status = Column(String, nullable=True)  # planned, in-progress, finished, cancelled
    class_code = Column(String, nullable=True)  # inpatient, outpatient, emergency, etc.
    priority = Column(String, nullable=True)

    # subject_reference = Column(String, nullable=True)  # Reference to Patient (Patient/123)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    types = relationship(
        "EncounterType", back_populates="encounter", cascade="all, delete-orphan"
    )
    participants = relationship(
        "EncounterParticipant", back_populates="encounter", cascade="all, delete-orphan"
    )
    diagnoses = relationship(
        "EncounterDiagnosis", back_populates="encounter", cascade="all, delete-orphan"
    )
    locations = relationship(
        "EncounterLocation", back_populates="encounter", cascade="all, delete-orphan"
    )
    reason_codes = relationship(
        "EncounterReasonCode", back_populates="encounter", cascade="all, delete-orphan"
    )

    patient = relationship("PatientModel", back_populates="encounters")


class EncounterType(Base):
    __tablename__ = "encounter_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    encounter_id = Column(
        Integer, ForeignKey("encounter.id"), nullable=False, index=True
    )

    coding_system = Column(String, nullable=True)
    coding_code = Column(String, nullable=True)
    coding_display = Column(String, nullable=True)
    text = Column(String, nullable=True)

    encounter = relationship("EncounterModel", back_populates="types")


class EncounterParticipant(Base):
    __tablename__ = "encounter_participant"

    id = Column(Integer, primary_key=True, autoincrement=True)

    encounter_id = Column(
        Integer, ForeignKey("encounter.id"), nullable=False, index=True
    )

    type_text = Column(
        String, nullable=True
    )  # e.g., "Primary Physician", "Consulting Physician"

    # individual_reference = Column(
    #     String, nullable=True
    # )  # Reference to Practitioner (Practitioner/456)

    reference_type = Column(
        Enum(ParticipantReferenceType, name="participant_reference_type"),
        nullable=True,
    )  # Patient, Practitioner, etc.
    # reference_id = Column(String, nullable=True)    # actual ID

    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=True)
    practitioner_id = Column(Integer, ForeignKey("practitioner.id"), nullable=True)

    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    encounter = relationship("EncounterModel", back_populates="participants")

    patient = relationship(
        "PatientModel",
        back_populates="encounter_participations",
        foreign_keys=[patient_id],
    )

    practitioner = relationship(
        "PractitionerModel",
        back_populates="encounter_participations",
        foreign_keys=[practitioner_id],
    )

    __table_args__ = (
        CheckConstraint(
            f"""
    (reference_type = '{ParticipantReferenceType.PATIENT.value}' AND patient_id IS NOT NULL AND practitioner_id IS NULL)
    OR
    (reference_type = '{ParticipantReferenceType.PRACTITIONER.value}' AND practitioner_id IS NOT NULL AND patient_id IS NULL)
    """,
            name="valid_reference_type_constraint",
        ),
    )


class EncounterDiagnosis(Base):
    __tablename__ = "encounter_diagnosis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    encounter_id = Column(
        Integer, ForeignKey("encounter.id"), nullable=False, index=True
    )

    condition_reference = Column(
        String, nullable=True
    )  # Reference to Condition resource
    use_text = Column(
        String, nullable=True
    )  # e.g., "admission", "discharge", "billing"
    rank = Column(String, nullable=True)  # Integer as string for simplicity

    encounter = relationship("EncounterModel", back_populates="diagnoses")


class EncounterLocation(Base):
    __tablename__ = "encounter_location"

    id = Column(Integer, primary_key=True, autoincrement=True)
    encounter_id = Column(
        Integer, ForeignKey("encounter.id"), nullable=False, index=True
    )

    location_reference = Column(String, nullable=True)  # Reference to Location
    status = Column(String, nullable=True)  # planned, active, reserved, completed
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    encounter = relationship("EncounterModel", back_populates="locations")


class EncounterReasonCode(Base):
    __tablename__ = "encounter_reason_code"

    id = Column(Integer, primary_key=True, autoincrement=True)
    encounter_id = Column(
        Integer, ForeignKey("encounter.id"), nullable=False, index=True
    )

    coding_system = Column(String, nullable=True)
    coding_code = Column(String, nullable=True)
    coding_display = Column(String, nullable=True)
    text = Column(String, nullable=True)

    encounter = relationship("EncounterModel", back_populates="reason_codes")
