# from sqlalchemy import Column, String, ForeignKey, Integer, Enum, DateTime
# from sqlalchemy.orm import relationship
# from app.core.database import FHIRBase as Base
# from app.models.enums import GenderType


# class PatientContact(Base):
#     __tablename__ = "patient_contact"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     patient_id = Column(
#         Integer,
#         ForeignKey("patient.id"),
#         nullable=False,
#         index=True,
#     )

#     gender = Column(
#         Enum(GenderType, name="patient_contact_gender"),
#         nullable=True,
#     )

#     organization_id = Column(Integer, nullable=True)

#     # relationships
#     patient = relationship("PatientModel", back_populates="contacts")

#     relationship_codes = relationship(
#         "PatientContactRelationship",
#         back_populates="contact",
#         cascade="all, delete-orphan",
#     )

#     telecoms = relationship(
#         "PatientContactTelecom",
#         back_populates="contact",
#         cascade="all, delete-orphan",
#     )

#     name = relationship(
#         "PatientContactHumanName",
#         back_populates="contact",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )

#     address = relationship(
#         "PatientContactAddress",
#         back_populates="contact",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )

#     period = relationship(
#         "PatientContactPeriod",
#         back_populates="contact",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )


# class PatientContactRelationship(Base):
#     __tablename__ = "patient_contact_relationship"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     contact_id = Column(
#         Integer,
#         ForeignKey("patient_contact.id"),
#         nullable=False,
#         index=True,
#     )

#     text = Column(String, nullable=True)

#     contact = relationship("PatientContact", back_populates="relationship_codes")

#     codings = relationship(
#         "PatientContactRelationshipCoding",
#         back_populates="relationship",
#         cascade="all, delete-orphan",
#     )


# class PatientContactRelationshipCoding(Base):
#     __tablename__ = "patient_contact_relationship_coding"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     relationship_id = Column(
#         Integer,
#         ForeignKey("patient_contact_relationship.id"),
#         nullable=False,
#         index=True,
#     )

#     system = Column(String, nullable=True)
#     version = Column(String, nullable=True)
#     code = Column(String, nullable=True)
#     display = Column(String, nullable=True)

#     relationship = relationship(
#         "PatientContactRelationship",
#         back_populates="codings",
#     )


# class PatientContactTelecom(Base):
#     __tablename__ = "patient_contact_telecom"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     contact_id = Column(
#         Integer,
#         ForeignKey("patient_contact.id"),
#         nullable=False,
#         index=True,
#     )

#     system = Column(String, nullable=True)
#     value = Column(String, nullable=True)
#     use = Column(String, nullable=True)
#     rank = Column(Integer, nullable=True)

#     contact = relationship("PatientContact", back_populates="telecoms")


# class PatientContactHumanName(Base):
#     __tablename__ = "patient_contact_name"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     contact_id = Column(
#         Integer,
#         ForeignKey("patient_contact.id"),
#         nullable=False,
#         unique=True,
#         index=True,
#     )

#     use = Column(String, nullable=True)
#     text = Column(String, nullable=True)
#     family = Column(String, nullable=True)

#     contact = relationship("PatientContact", back_populates="name")

#     given = relationship(
#         "PatientContactHumanNameGiven",
#         back_populates="name",
#         cascade="all, delete-orphan",
#     )

#     prefix = relationship(
#         "PatientContactHumanNamePrefix",
#         back_populates="name",
#         cascade="all, delete-orphan",
#     )

#     suffix = relationship(
#         "PatientContactHumanNameSuffix",
#         back_populates="name",
#         cascade="all, delete-orphan",
#     )

#     period = relationship(
#         "PatientContactHumanNamePeriod",
#         back_populates="name",
#         uselist=False,
#         cascade="all, delete-orphan",
#     )


# class PatientContactHumanNameGiven(Base):
#     __tablename__ = "patient_contact_name_given"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     name_id = Column(
#         Integer,
#         ForeignKey("patient_contact_name.id"),
#         nullable=False,
#         index=True,
#     )

#     value = Column(String, nullable=True)

#     name = relationship("PatientContactHumanName", back_populates="given")


# class PatientContactHumanNamePrefix(Base):
#     __tablename__ = "patient_contact_name_prefix"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     name_id = Column(
#         Integer,
#         ForeignKey("patient_contact_name.id"),
#         nullable=False,
#         index=True,
#     )

#     value = Column(String, nullable=True)

#     name = relationship("PatientContactHumanName", back_populates="prefix")


# class PatientContactHumanNameSuffix(Base):
#     __tablename__ = "patient_contact_name_suffix"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     name_id = Column(
#         Integer,
#         ForeignKey("patient_contact_name.id"),
#         nullable=False,
#         index=True,
#     )

#     value = Column(String, nullable=True)

#     name = relationship("PatientContactHumanName", back_populates="suffix")


# class PatientContactHumanNamePeriod(Base):
#     __tablename__ = "patient_contact_name_period"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     name_id = Column(
#         Integer,
#         ForeignKey("patient_contact_name.id"),
#         nullable=False,
#         unique=True,
#         index=True,
#     )

#     start = Column(DateTime, nullable=True)
#     end = Column(DateTime, nullable=True)

#     name = relationship("PatientContactHumanName", back_populates="period")


# class PatientContactAddress(Base):
#     __tablename__ = "patient_contact_address"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     contact_id = Column(
#         Integer,
#         ForeignKey("patient_contact.id"),
#         nullable=False,
#         unique=True,
#     )

#     text = Column(String, nullable=True)
#     city = Column(String, nullable=True)
#     state = Column(String, nullable=True)
#     postal_code = Column(String, nullable=True)
#     country = Column(String, nullable=True)

#     contact = relationship("PatientContact", back_populates="address")


# class PatientContactPeriod(Base):
#     __tablename__ = "patient_contact_period"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     contact_id = Column(
#         Integer,
#         ForeignKey("patient_contact.id"),
#         nullable=False,
#         unique=True,
#     )

#     start = Column(String, nullable=True)
#     end = Column(String, nullable=True)

#     contact = relationship("PatientContact", back_populates="period")
