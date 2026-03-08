# from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Enum
# from sqlalchemy.orm import relationship
# from app.core.database import FHIRBase as Base
# from app.models.patient.enums import (
#     PatientTelecomContactPointSystem,
#     PatientTelecomContactPointUse,
# )


# class PatientTelecom(Base):
#     __tablename__ = "patient_telecom"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

#     system = Column(
#         Enum(
#             PatientTelecomContactPointSystem,
#             name="patient_telecom_contact_point_system",
#         ),
#         nullable=True,
#     )
#     value = Column(String, nullable=True)
#     use = Column(
#         Enum(PatientTelecomContactPointUse, name="patient_telecom_contact_point_use"),
#         nullable=True,
#     )
#     rank = Column(Integer, nullable=True)

#     # relationships
#     patient = relationship("PatientModel", back_populates="telecoms")

#     period = relationship(
#         "PatientTelecomPeriod",
#         back_populates="telecom",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )


# class PatientTelecomPeriod(Base):
#     __tablename__ = "patient_telecom_period"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     telecom_id = Column(
#         Integer,
#         ForeignKey("patient_telecom.id"),
#         nullable=False,
#         unique=True,  # one-to-one
#     )

#     start = Column(DateTime, nullable=True)
#     end = Column(DateTime, nullable=True)

#     telecom = relationship("PatientTelecom", back_populates="period")
