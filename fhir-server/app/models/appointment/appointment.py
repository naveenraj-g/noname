# from sqlalchemy import Column, Date, Boolean, Integer, String, DateTime, Enum, Sequence
# from app.core.database import FHIRBase as Base
# from .enums import AppointmentStatus


# class AppointmentModel(Base):
#     __tablename__ = "appointment"

#     id = Column(Integer, primary_key=True, autoincrement=True, index=True)

#     status = Column(
#         Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.proposed
#     )
