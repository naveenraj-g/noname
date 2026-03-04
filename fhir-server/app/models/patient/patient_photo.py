from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from app.core.database import FHIRBase as Base


class PatientPhoto(Base):
    __tablename__ = "patient_photo"

    id = Column(Integer, primary_key=True, autoincrement=True)

    patient_id = Column(
        Integer,
        ForeignKey("patient.id"),
        nullable=False,
        index=True,
    )

    content_type = Column(String, nullable=True)
    language = Column(String, nullable=True)

    data = Column(LargeBinary, nullable=True)  # base64 decoded binary
    url = Column(String, nullable=True)

    size = Column(Integer, nullable=True)
    hash = Column(String, nullable=True)

    title = Column(String, nullable=True)
    creation = Column(DateTime, nullable=True)

    # relationships
    patient = relationship("PatientModel", back_populates="photos")
