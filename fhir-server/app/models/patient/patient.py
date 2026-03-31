from sqlalchemy import Column, Date, Boolean, Integer, String, DateTime, Enum, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import FHIRBase as Base
from app.models.enums import GenderType

# class PatientModel(Base):
#     __tablename__ = "patient"

#     id = Column(Integer, primary_key=True, autoincrement=True, index=True)
#     orgId = Column(Integer, nullable=False)

#     active = Column(Boolean, nullable=True)
#     gender = Column(Enum(GenderType, name="gender_type"), nullable=True)
#     birth_date = Column(Date, nullable=True)

#     deceased_boolean = Column(Boolean, nullable=True)
#     deceased_dateTime = Column(DateTime, nullable=True)

#     multiple_birth_boolean = Column(Boolean, nullable=True)
#     multiple_birth_integer = Column(Integer, nullable=True)

#     managing_organization_id = Column(Integer, nullable=True)  # Organization reference

#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())

#     # Relationships
#     identifiers = relationship(
#         "PatientIdentifier", back_populates="patient", cascade="all, delete-orphan"
#     )

#     names = relationship(
#         "PatientName", back_populates="patient", cascade="all, delete-orphan"
#     )

#     telecoms = relationship(
#         "PatientTelecom", back_populates="patient", cascade="all, delete-orphan"
#     )

#     addresses = relationship(
#         "PatientAddress", back_populates="patient", cascade="all, delete-orphan"
#     )

#     marital_status = relationship(
#         "PatientMaritalStatus",
#         back_populates="patient",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )

#     photos = relationship(
#         "PatientPhoto",
#         back_populates="patient",
#         cascade="all, delete-orphan",
#     )

#     contacts = relationship(
#         "PatientContact",
#         back_populates="patient",
#         cascade="all, delete-orphan",
#     )

#     communications = relationship(
#         "PatientCommunication",
#         back_populates="patient",
#         cascade="all, delete-orphan",
#     )

#     general_practitioners = relationship(
#         "PatientGeneralPractitioner",
#         back_populates="patient",
#         cascade="all, delete-orphan",
#     )

#     links = relationship(
#         "PatientLink",
#         back_populates="patient",
#         cascade="all, delete-orphan",
#     )

patient_id_seq = Sequence("patient_id_seq", start=10000, increment=1)


class PatientModel(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    patient_id = Column(
        Integer,
        patient_id_seq,
        server_default=patient_id_seq.next_value(),
        unique=True,
        index=True,
    )
    user_id = Column(String, nullable=True)
    org_id = Column(String, nullable=True)
    active = Column(Boolean, nullable=True)
    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    gender = Column(Enum(GenderType, name="gender_type"), nullable=True)
    birth_date = Column(Date, nullable=True)
    deceased_boolean = Column(Boolean, nullable=True)
    deceased_dateTime = Column(DateTime, nullable=True)
    marital_status = Column(String, nullable=True)
