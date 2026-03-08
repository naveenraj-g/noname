# from sqlalchemy import Column, ForeignKey, Integer, Enum
# from sqlalchemy.orm import relationship
# from app.core.database import FHIRBase as Base
# from app.models.patient.enums import PatientLinkOtherRefType, PatientLinkType


# class PatientLink(Base):
#     __tablename__ = "patient_link"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

#     other_ref_type = Column(
#         Enum(PatientLinkOtherRefType), name="patient_link_other_ref_type"
#     )  # Patient | RelatedPerson
#     other_ref_id = Column(Integer)
#     type = Column(
#         Enum(PatientLinkType), name="patient_link_type"
#     )  # replaces | replaced-by | refer | seealso

#     patient = relationship("PatientModel", back_populates="links")
