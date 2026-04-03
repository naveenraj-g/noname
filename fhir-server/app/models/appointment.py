from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import FHIRBase as Base

appointment_id_seq = Sequence("appointment_id_seq", start=40000, increment=1)


class AppointmentModel(Base):
    __tablename__ = "appointment"

    # Internal PK — never exposed
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Public ID — used in all API responses and FHIR output
    appointment_id = Column(
        Integer,
        appointment_id_seq,
        server_default=appointment_id_seq.next_value(),
        unique=True,
        index=True,
        nullable=False,
    )

    user_id = Column(String, nullable=True, index=True)
    org_id = Column(String, nullable=True, index=True)

    # Required
    status = Column(String, nullable=False)  # proposed | pending | booked | arrived | fulfilled | cancelled | noshow | entered-in-error | checked-in | waitlist

    # Scheduling
    start = Column(DateTime(timezone=True), nullable=True)
    end = Column(DateTime(timezone=True), nullable=True)
    minutes_duration = Column(Integer, nullable=True)
    created = Column(DateTime(timezone=True), nullable=True)

    # Descriptive
    description = Column(Text, nullable=True)
    patient_instruction = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    priority_value = Column(Integer, nullable=True)

    # Service / type (stored as flat coded values)
    service_category_code = Column(String, nullable=True)
    service_category_display = Column(String, nullable=True)
    service_type_code = Column(String, nullable=True)
    service_type_display = Column(String, nullable=True)
    specialty_code = Column(String, nullable=True)
    specialty_display = Column(String, nullable=True)
    appointment_type_code = Column(String, nullable=True)
    appointment_type_display = Column(String, nullable=True)

    # Subject (Patient reference)
    subject_reference = Column(String, nullable=True)  # e.g. "Patient/123"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    participants = relationship(
        "AppointmentParticipant", back_populates="appointment", cascade="all, delete-orphan"
    )
    reason_codes = relationship(
        "AppointmentReasonCode", back_populates="appointment", cascade="all, delete-orphan"
    )


class AppointmentParticipant(Base):
    __tablename__ = "appointment_participant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey("appointment.id"), nullable=False, index=True)
    org_id = Column(String, nullable=True)

    actor_reference = Column(String, nullable=True)   # e.g. "Patient/123", "Practitioner/456"
    actor_display = Column(String, nullable=True)

    type_code = Column(String, nullable=True)
    type_display = Column(String, nullable=True)
    type_text = Column(String, nullable=True)

    required = Column(String, nullable=True)  # required | optional | information-only
    status = Column(String, nullable=False, default="needs-action")  # accepted | declined | tentative | needs-action

    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    appointment = relationship("AppointmentModel", back_populates="participants")


class AppointmentReasonCode(Base):
    __tablename__ = "appointment_reason_code"

    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey("appointment.id"), nullable=False, index=True)
    org_id = Column(String, nullable=True)

    coding_system = Column(String, nullable=True)
    coding_code = Column(String, nullable=True)
    coding_display = Column(String, nullable=True)
    text = Column(String, nullable=True)

    appointment = relationship("AppointmentModel", back_populates="reason_codes")
