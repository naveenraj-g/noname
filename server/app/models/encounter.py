
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class EncounterModel(Base):
    __tablename__ = "encounter"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=True)  # planned, in-progress, finished, cancelled
    class_code = Column(String, nullable=True)  # inpatient, outpatient, emergency, etc.
    priority = Column(String, nullable=True)
    # subject_reference = Column(String, nullable=True)  # Reference to Patient (Patient/123)
    patient_id = Column(String, ForeignKey("patient.id"), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    types = relationship("EncounterType", back_populates="encounter", cascade="all, delete-orphan")
    participants = relationship("EncounterParticipant", back_populates="encounter", cascade="all, delete-orphan")
    diagnoses = relationship("EncounterDiagnosis", back_populates="encounter", cascade="all, delete-orphan")
    locations = relationship("EncounterLocation", back_populates="encounter", cascade="all, delete-orphan")
    reason_codes = relationship("EncounterReasonCode", back_populates="encounter", cascade="all, delete-orphan")

    patient = relationship("PatientModel", back_populates="encounters")

class EncounterType(Base):
    __tablename__ = "encounter_type"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    encounter_id = Column(String, ForeignKey("encounter.id"), nullable=False, index=True)
    
    coding_system = Column(String, nullable=True)
    coding_code = Column(String, nullable=True)
    coding_display = Column(String, nullable=True)
    text = Column(String, nullable=True)
    
    encounter = relationship("EncounterModel", back_populates="types")

class EncounterParticipant(Base):
    __tablename__ = "encounter_participant"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    encounter_id = Column(String, ForeignKey("encounter.id"), nullable=False, index=True)
    
    type_text = Column(String, nullable=True)  # e.g., "Primary Physician", "Consulting Physician"
    individual_reference = Column(String, nullable=True)  # Reference to Practitioner (Practitioner/456)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    encounter = relationship("EncounterModel", back_populates="participants")

class EncounterDiagnosis(Base):
    __tablename__ = "encounter_diagnosis"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    encounter_id = Column(String, ForeignKey("encounter.id"), nullable=False, index=True)
    
    condition_reference = Column(String, nullable=True)  # Reference to Condition resource
    use_text = Column(String, nullable=True)  # e.g., "admission", "discharge", "billing"
    rank = Column(String, nullable=True)  # Integer as string for simplicity
    
    encounter = relationship("EncounterModel", back_populates="diagnoses")

class EncounterLocation(Base):
    __tablename__ = "encounter_location"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    encounter_id = Column(String, ForeignKey("encounter.id"), nullable=False, index=True)
    
    location_reference = Column(String, nullable=True)  # Reference to Location
    status = Column(String, nullable=True)  # planned, active, reserved, completed
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    encounter = relationship("EncounterModel", back_populates="locations")

class EncounterReasonCode(Base):
    __tablename__ = "encounter_reason_code"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    encounter_id = Column(String, ForeignKey("encounter.id"), nullable=False, index=True)
    
    coding_system = Column(String, nullable=True)
    coding_code = Column(String, nullable=True)
    coding_display = Column(String, nullable=True)
    text = Column(String, nullable=True)
    
    encounter = relationship("EncounterModel", back_populates="reason_codes")
