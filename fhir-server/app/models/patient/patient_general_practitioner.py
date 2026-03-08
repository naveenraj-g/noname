# from sqlalchemy import Column, ForeignKey, Integer, Enum
# from sqlalchemy.orm import relationship
# from app.core.database import FHIRBase as Base
# from app.models.patient.enums import PatientGeneralPractitionerRefType


# class PatientGeneralPractitioner(Base):
#     __tablename__ = "patient_general_practitioner"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

#     ref_type = Column(
#         Enum(PatientGeneralPractitionerRefType),
#         name="patient_general_practitioner_ref_type",
#     )  # Practitioner | PractitionerRole | Organization
#     ref_id = Column(Integer, index=True)

#     patient = relationship("PatientModel", back_populates="general_practitioners")
