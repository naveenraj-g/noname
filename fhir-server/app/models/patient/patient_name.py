from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from app.core.database import FHIRBase as Base


class PatientName(Base):
    __tablename__ = "patient_name"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

    use = Column(String, nullable=True)
    text = Column(String, nullable=True)
    family = Column(String, nullable=True)

    # relationships
    patient = relationship("PatientModel", back_populates="names")

    given = relationship(
        "PatientNameGiven",
        back_populates="name",
        cascade="all, delete-orphan",
    )

    prefix = relationship(
        "PatientNamePrefix",
        back_populates="name",
        cascade="all, delete-orphan",
    )

    suffix = relationship(
        "PatientNameSuffix",
        back_populates="name",
        cascade="all, delete-orphan",
    )

    period = relationship(
        "PatientNamePeriod",
        back_populates="human_name",
        uselist=False,
        cascade="all, delete-orphan",
    )


class PatientNameGiven(Base):
    __tablename__ = "patient_name_given"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_id = Column(
        Integer,
        ForeignKey("patient_name.id"),
        nullable=False,
        index=True,
    )

    value = Column(String, nullable=True)

    human_name = relationship("PatientName", back_populates="given")


class PatientNamePrefix(Base):
    __tablename__ = "patient_name_prefix"

    id = Column(Integer, primary_key=True, autoincrement=True)
    human_name_id = Column(
        Integer,
        ForeignKey("patient_name.id"),
        nullable=False,
        index=True,
    )

    value = Column(String, nullable=True)

    human_name = relationship("PatientName", back_populates="prefix")


class PatientNameSuffix(Base):
    __tablename__ = "patient_name_suffix"

    id = Column(Integer, primary_key=True, autoincrement=True)
    human_name_id = Column(
        Integer,
        ForeignKey("patient_name.id"),
        nullable=False,
        index=True,
    )

    value = Column(String, nullable=True)

    human_name = relationship("PatientName", back_populates="suffix")


class PatientNamePeriod(Base):
    __tablename__ = "patient_name_period"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name_id = Column(
        Integer,
        ForeignKey("patient_name.id"),
        nullable=False,
        unique=True,  # one-to-one
    )

    start = Column(DateTime, nullable=True)
    end = Column(DateTime, nullable=True)

    name = relationship("PatientName", back_populates="period")
