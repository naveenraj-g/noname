from sqlalchemy import Column, Date, DateTime, Float, Integer, Sequence, String
from sqlalchemy.sql import func

from app.core.database import FHIRBase as Base

vitals_id_seq = Sequence("vitals_id_seq", start=70000, increment=1)


class VitalsModel(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    vitals_id = Column(
        Integer,
        vitals_id_seq,
        server_default=vitals_id_seq.next_value(),
        unique=True,
        index=True,
        nullable=False,
    )

    # Identity
    pseudo_id = Column(String, nullable=True, index=True)
    pseudo_id2 = Column(String, nullable=True)
    user_id = Column(String, nullable=True, index=True)
    patient_id = Column(Integer, nullable=True, index=True)
    org_id = Column(String, nullable=True, index=True)

    # Temporal
    date = Column(Date, nullable=True)
    datetime = Column(DateTime(timezone=True), nullable=True)

    # Activity
    activity_name = Column(String, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    avg_hr_bpm = Column(Integer, nullable=True)
    max_hr_bpm = Column(Integer, nullable=True)
    elevation_gain_m = Column(Float, nullable=True)
    distance_meters = Column(Float, nullable=True)
    calories_kcal = Column(Float, nullable=True)
    steps = Column(Integer, nullable=True)
    speed_mps = Column(Float, nullable=True)

    # Active zone minutes
    active_zone_minutes = Column(Integer, nullable=True)
    fatburn_active_zone_minutes = Column(Integer, nullable=True)
    cardio_active_zone_minutes = Column(Integer, nullable=True)
    peak_active_zone_minutes = Column(Integer, nullable=True)

    # Demographics
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)

    # Heart / stress
    resting_heart_rate = Column(Integer, nullable=True)
    heart_rate_variability = Column(Float, nullable=True)
    stress_management_score = Column(Integer, nullable=True)

    # Sleep
    sleep_minutes = Column(Integer, nullable=True)
    rem_sleep_minutes = Column(Integer, nullable=True)
    deep_sleep_minutes = Column(Integer, nullable=True)
    awake_minutes = Column(Integer, nullable=True)
    light_sleep_minutes = Column(Integer, nullable=True)
    bed_time = Column(DateTime(timezone=True), nullable=True)
    wake_up_time = Column(DateTime(timezone=True), nullable=True)
    deep_sleep_percent = Column(Float, nullable=True)
    rem_sleep_percent = Column(Float, nullable=True)
    awake_percent = Column(Float, nullable=True)
    light_sleep_percent = Column(Float, nullable=True)

    summary = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
