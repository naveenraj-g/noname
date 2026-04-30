from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VitalsCreateSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "pseudo_id": "user_12345",
                "pseudo_id2": "device_fitbit_67890",
                "date": "2026-04-29",
                "datetime": "2026-04-29T07:30:00Z",
                "activity_name": "Walking",
                "duration_minutes": 45.5,
                "start_time": "2026-04-29T06:45:00Z",
                "end_time": "2026-04-29T07:30:30Z",
                "avg_hr_bpm": 72,
                "max_hr_bpm": 120,
                "elevation_gain_m": 12.5,
                "distance_meters": 5000,
                "calories_kcal": 350.5,
                "steps": 10234,
                "speed_mps": 1.4,
                "active_zone_minutes": 30,
                "fatburn_active_zone_minutes": 15,
                "cardio_active_zone_minutes": 10,
                "peak_active_zone_minutes": 5,
                "age": 30,
                "gender": "male",
                "weight_kg": 75.2,
                "height_cm": 180.0,
                "resting_heart_rate": 60,
                "heart_rate_variability": 45.5,
                "stress_management_score": 80,
                "sleep_minutes": 420,
                "rem_sleep_minutes": 90,
                "deep_sleep_minutes": 60,
                "awake_minutes": 20,
                "light_sleep_minutes": 250,
                "bed_time": "2026-04-28T22:30:00Z",
                "wake_up_time": "2026-04-29T05:30:00Z",
                "deep_sleep_percent": 14.3,
                "rem_sleep_percent": 21.4,
                "awake_percent": 4.8,
                "light_sleep_percent": 59.5,
            }
        },
    )

    # Identity
    pseudo_id: Optional[str] = None
    pseudo_id2: Optional[str] = None
    patient_id: Optional[int] = Field(None, description="Public patient_id.")

    summary: Optional[str] = None

    # Temporal
    date: Optional[date] = None
    datetime: Optional[datetime] = None

    # Activity
    activity_name: Optional[str] = None
    duration_minutes: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    avg_hr_bpm: Optional[int] = None
    max_hr_bpm: Optional[int] = None
    elevation_gain_m: Optional[float] = None
    distance_meters: Optional[float] = None
    calories_kcal: Optional[float] = None
    steps: Optional[int] = None
    speed_mps: Optional[float] = None

    # Active zone minutes
    active_zone_minutes: Optional[int] = None
    fatburn_active_zone_minutes: Optional[int] = None
    cardio_active_zone_minutes: Optional[int] = None
    peak_active_zone_minutes: Optional[int] = None

    # Demographics
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None

    # Heart / stress
    resting_heart_rate: Optional[int] = None
    heart_rate_variability: Optional[float] = None
    stress_management_score: Optional[int] = None

    # Sleep
    sleep_minutes: Optional[int] = None
    rem_sleep_minutes: Optional[int] = None
    deep_sleep_minutes: Optional[int] = None
    awake_minutes: Optional[int] = None
    light_sleep_minutes: Optional[int] = None
    bed_time: Optional[datetime] = None
    wake_up_time: Optional[datetime] = None
    deep_sleep_percent: Optional[float] = None
    rem_sleep_percent: Optional[float] = None
    awake_percent: Optional[float] = None
    light_sleep_percent: Optional[float] = None


class VitalsPatchSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Identity
    pseudo_id: Optional[str] = None
    pseudo_id2: Optional[str] = None
    patient_id: Optional[int] = None

    summary: Optional[str] = None

    # Temporal
    date: Optional[date] = None
    datetime: Optional[datetime] = None

    # Activity
    activity_name: Optional[str] = None
    duration_minutes: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    avg_hr_bpm: Optional[int] = None
    max_hr_bpm: Optional[int] = None
    elevation_gain_m: Optional[float] = None
    distance_meters: Optional[float] = None
    calories_kcal: Optional[float] = None
    steps: Optional[int] = None
    speed_mps: Optional[float] = None

    # Active zone minutes
    active_zone_minutes: Optional[int] = None
    fatburn_active_zone_minutes: Optional[int] = None
    cardio_active_zone_minutes: Optional[int] = None
    peak_active_zone_minutes: Optional[int] = None

    # Demographics
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None

    # Heart / stress
    resting_heart_rate: Optional[int] = None
    heart_rate_variability: Optional[float] = None
    stress_management_score: Optional[int] = None

    # Sleep
    sleep_minutes: Optional[int] = None
    rem_sleep_minutes: Optional[int] = None
    deep_sleep_minutes: Optional[int] = None
    awake_minutes: Optional[int] = None
    light_sleep_minutes: Optional[int] = None
    bed_time: Optional[datetime] = None
    wake_up_time: Optional[datetime] = None
    deep_sleep_percent: Optional[float] = None
    rem_sleep_percent: Optional[float] = None
    awake_percent: Optional[float] = None
    light_sleep_percent: Optional[float] = None


class VitalsResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(..., description="Public vitals identifier.")

    # Identity
    pseudo_id: Optional[str] = None
    pseudo_id2: Optional[str] = None
    user_id: Optional[str] = None
    patient_id: Optional[int] = None
    org_id: Optional[str] = None

    summary: Optional[str] = None

    # Temporal
    date: Optional[date] = None
    datetime: Optional[datetime] = None

    # Activity
    activity_name: Optional[str] = None
    duration_minutes: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    avg_hr_bpm: Optional[int] = None
    max_hr_bpm: Optional[int] = None
    elevation_gain_m: Optional[float] = None
    distance_meters: Optional[float] = None
    calories_kcal: Optional[float] = None
    steps: Optional[int] = None
    speed_mps: Optional[float] = None

    # Active zone minutes
    active_zone_minutes: Optional[int] = None
    fatburn_active_zone_minutes: Optional[int] = None
    cardio_active_zone_minutes: Optional[int] = None
    peak_active_zone_minutes: Optional[int] = None

    # Demographics
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None

    # Heart / stress
    resting_heart_rate: Optional[int] = None
    heart_rate_variability: Optional[float] = None
    stress_management_score: Optional[int] = None

    # Sleep
    sleep_minutes: Optional[int] = None
    rem_sleep_minutes: Optional[int] = None
    deep_sleep_minutes: Optional[int] = None
    awake_minutes: Optional[int] = None
    light_sleep_minutes: Optional[int] = None
    bed_time: Optional[datetime] = None
    wake_up_time: Optional[datetime] = None
    deep_sleep_percent: Optional[float] = None
    rem_sleep_percent: Optional[float] = None
    awake_percent: Optional[float] = None
    light_sleep_percent: Optional[float] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
