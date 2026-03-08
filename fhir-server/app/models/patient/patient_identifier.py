# from sqlalchemy import (
#     Column,
#     String,
#     ForeignKey,
#     Integer,
#     DateTime,
#     Enum,
# )
# from sqlalchemy.orm import relationship
# from app.core.database import FHIRBase as Base
# from app.models.enums import IdentifierUse


# class PatientIdentifier(Base):
#     __tablename__ = "patient_identifier"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

#     use = Column(Enum(IdentifierUse, name="identifier_use"), nullable=True)
#     system = Column(String, nullable=True)
#     value = Column(String, nullable=True)
#     assigner = Column(Integer, nullable=True)

#     # relationships
#     patient = relationship("PatientModel", back_populates="identifiers")

#     type = relationship(
#         "IdentifierType",
#         back_populates="identifier",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )

#     period = relationship(
#         "PatientIdentifierPeriod",
#         back_populates="identifier",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )


# class IdentifierType(Base):
#     """
#     FHIR CodeableConcept
#     """

#     __tablename__ = "identifier_type"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     identifier_id = Column(
#         Integer,
#         ForeignKey("patient_identifier.id"),
#         nullable=False,
#         unique=True,  # one-to-one
#     )

#     text = Column(String, nullable=True)

#     identifier = relationship("PatientIdentifier", back_populates="type")

#     codings = relationship(
#         "IdentifierTypeCoding",
#         back_populates="type",
#         cascade="all, delete-orphan",
#     )


# class IdentifierTypeCoding(Base):
#     """
#     FHIR Coding
#     """

#     __tablename__ = "identifier_type_coding"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     type_id = Column(Integer, ForeignKey("identifier_type.id"), nullable=False)

#     system = Column(String, nullable=True)
#     version = Column(String, nullable=True)
#     code = Column(String, nullable=True)
#     display = Column(String, nullable=True)
#     user_selected = Column(String, nullable=True)

#     type = relationship("IdentifierType", back_populates="codings")


# class PatientIdentifierPeriod(Base):
#     """
#     FHIR Period
#     """

#     __tablename__ = "patient_identifier_period"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     identifier_id = Column(
#         Integer,
#         ForeignKey("patient_identifier.id"),
#         nullable=False,
#         unique=True,  # one-to-one
#     )

#     start = Column(DateTime, nullable=True)
#     end = Column(DateTime, nullable=True)

#     identifier = relationship("PatientIdentifier", back_populates="period")
