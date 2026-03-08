# from sqlalchemy import Column, String, ForeignKey, Integer, Enum, DateTime
# from sqlalchemy.orm import relationship
# from app.core.database import FHIRBase as Base
# from app.models.patient.enums import PatientAddressUse, PatientAddressType


# class PatientAddress(Base):
#     __tablename__ = "patient_address"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     patient_id = Column(Integer, ForeignKey("patient.id"), nullable=False, index=True)

#     use = Column(Enum(PatientAddressUse, name="patient_address_use"), nullable=True)
#     type = Column(Enum(PatientAddressType, name="patient_address_type"), nullable=True)
#     text = Column(String, nullable=True)
#     city = Column(String, nullable=True)
#     district = Column(String, nullable=True)
#     state = Column(String, nullable=True)
#     postal_code = Column(String, nullable=True)
#     country = Column(String, nullable=True)

#     # relationships
#     patient = relationship("PatientModel", back_populates="addresses")

#     # line[]
#     lines = relationship(
#         "PatientAddressLine",
#         back_populates="address",
#         cascade="all, delete-orphan",
#     )

#     # period
#     period = relationship(
#         "PatientAddressPeriod",
#         back_populates="address",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )


# class PatientAddressLine(Base):
#     __tablename__ = "patient_address_line"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     address_id = Column(
#         Integer,
#         ForeignKey("patient_address.id"),
#         nullable=False,
#         index=True,
#     )

#     value = Column(String, nullable=True)

#     address = relationship("PatientAddress", back_populates="lines")


# class PatientAddressPeriod(Base):
#     __tablename__ = "patient_address_period"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     address_id = Column(
#         Integer,
#         ForeignKey("patient_address.id"),
#         nullable=False,
#         unique=True,  # one-to-one
#         index=True,
#     )

#     start = Column(DateTime, nullable=True)
#     end = Column(DateTime, nullable=True)

#     address = relationship("PatientAddress", back_populates="period")
