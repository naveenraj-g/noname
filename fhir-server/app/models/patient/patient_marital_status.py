from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from app.core.database import FHIRBase as Base


class PatientMaritalStatus(Base):
    __tablename__ = "patient_marital_status"

    id = Column(Integer, primary_key=True, autoincrement=True)

    patient_id = Column(
        Integer,
        ForeignKey("patient.id"),
        nullable=False,
        unique=True,  # one-to-one
        index=True,
    )

    text = Column(String, nullable=True)

    patient = relationship("PatientModel", back_populates="marital_status")

    codings = relationship(
        "PatientMaritalStatusCoding",
        back_populates="marital_status",
        cascade="all, delete-orphan",
    )


class PatientMaritalStatusCoding(Base):
    __tablename__ = "patient_marital_status_coding"

    id = Column(Integer, primary_key=True, autoincrement=True)

    marital_status_id = Column(
        Integer,
        ForeignKey("patient_marital_status.id"),
        nullable=False,
        index=True,
    )

    system = Column(String, nullable=True)
    version = Column(String, nullable=True)
    code = Column(String, nullable=True)
    display = Column(String, nullable=True)
    user_selected = Column(Boolean, nullable=True)

    marital_status = relationship(
        "PatientMaritalStatus",
        back_populates="codings",
    )
