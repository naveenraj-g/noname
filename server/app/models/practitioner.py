from sqlalchemy import Column, String, Date, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import FHIRBase as Base


class PractitionerModel(Base):
    __tablename__ = "practitioner"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    active = Column(Boolean, nullable=True)
    gender = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    identifiers = relationship(
        "PractitionerIdentifier",
        back_populates="practitioner",
        cascade="all, delete-orphan",
    )
    names = relationship(
        "PractitionerName", back_populates="practitioner", cascade="all, delete-orphan"
    )
    telecoms = relationship(
        "PractitionerTelecom",
        back_populates="practitioner",
        cascade="all, delete-orphan",
    )
    addresses = relationship(
        "PractitionerAddress",
        back_populates="practitioner",
        cascade="all, delete-orphan",
    )
    qualifications = relationship(
        "PractitionerQualification",
        back_populates="practitioner",
        cascade="all, delete-orphan",
    )

    encounter_participations = relationship(
        "EncounterParticipant",
        back_populates="practitioner",
        foreign_keys="EncounterParticipant.practitioner_id",
    )


class PractitionerIdentifier(Base):
    __tablename__ = "practitioner_identifier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(
        Integer, ForeignKey("practitioner.id"), nullable=False, index=True
    )

    system = Column(String, nullable=True)
    value = Column(String, nullable=True)
    use = Column(String, nullable=True)

    practitioner = relationship("PractitionerModel", back_populates="identifiers")


class PractitionerName(Base):
    __tablename__ = "practitioner_name"

    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(
        Integer, ForeignKey("practitioner.id"), nullable=False, index=True
    )

    use = Column(String, nullable=True)
    family = Column(String, nullable=True)
    given = Column(String, nullable=True)  # Comma-separated
    text = Column(String, nullable=True)
    prefix = Column(String, nullable=True)  # Dr., Mr., Mrs., etc (comma-separated)
    suffix = Column(String, nullable=True)  # Jr., Sr., PhD, etc (comma-separated)

    practitioner = relationship("PractitionerModel", back_populates="names")


class PractitionerTelecom(Base):
    __tablename__ = "practitioner_telecom"

    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(
        Integer, ForeignKey("practitioner.id"), nullable=False, index=True
    )

    system = Column(String, nullable=True)
    value = Column(String, nullable=True)
    use = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)

    practitioner = relationship("PractitionerModel", back_populates="telecoms")


class PractitionerAddress(Base):
    __tablename__ = "practitioner_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(
        Integer, ForeignKey("practitioner.id"), nullable=False, index=True
    )

    use = Column(String, nullable=True)
    type = Column(String, nullable=True)
    text = Column(String, nullable=True)
    line = Column(String, nullable=True)  # Comma separated
    city = Column(String, nullable=True)
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)

    practitioner = relationship("PractitionerModel", back_populates="addresses")


class PractitionerQualification(Base):
    __tablename__ = "practitioner_qualification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(
        Integer, ForeignKey("practitioner.id"), nullable=False, index=True
    )

    identifier_system = Column(String, nullable=True)
    identifier_value = Column(String, nullable=True)
    code_text = Column(
        String, nullable=True
    )  # e.g., "MD", "PhD", "Board Certified in Cardiology"
    issuer = Column(String, nullable=True)  # Organization that issued the qualification

    practitioner = relationship("PractitionerModel", back_populates="qualifications")
