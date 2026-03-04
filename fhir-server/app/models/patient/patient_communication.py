from sqlalchemy import Column, ForeignKey, Integer, Boolean, String
from sqlalchemy.orm import relationship
from app.core.database import FHIRBase as Base


class PatientCommunication(Base):
    __tablename__ = "patient_communication"

    id = Column(Integer, primary_key=True, autoincrement=True)

    patient_id = Column(
        Integer,
        ForeignKey("patient.id"),
        nullable=False,
        index=True,
    )

    preferred = Column(Boolean, nullable=True)

    # relationships
    patient = relationship("PatientModel", back_populates="communications")

    language = relationship(
        "PatientCommunicationLanguage",
        back_populates="communication",
        uselist=False,
        cascade="all, delete-orphan",
    )


class PatientCommunicationLanguage(Base):
    __tablename__ = "patient_communication_language"

    id = Column(Integer, primary_key=True, autoincrement=True)

    communication_id = Column(
        Integer,
        ForeignKey("patient_communication.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    text = Column(String, nullable=True)

    communication = relationship(
        "PatientCommunication",
        back_populates="language",
    )

    codings = relationship(
        "PatientCommunicationLanguageCoding",
        back_populates="language",
        cascade="all, delete-orphan",
    )


class PatientCommunicationLanguageCoding(Base):
    __tablename__ = "patient_communication_language_coding"

    id = Column(Integer, primary_key=True, autoincrement=True)

    language_id = Column(
        Integer,
        ForeignKey("patient_communication_language.id"),
        nullable=False,
        index=True,
    )

    system = Column(String, nullable=True)
    version = Column(String, nullable=True)
    code = Column(String, nullable=True)
    display = Column(String, nullable=True)
    user_selected = Column(Boolean, nullable=True)

    language = relationship(
        "PatientCommunicationLanguage",
        back_populates="codings",
    )
