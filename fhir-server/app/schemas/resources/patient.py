from datetime import date, datetime
from typing import Optional
from pydantic import Field, ConfigDict
from typing_extensions import Literal
from app.schemas.base import FHIRBaseModel
from app.schemas.resources.base_resource import (
    FHIRCreateSchema,
    FHIRResponseSchema,
)
from app.schemas.enums import AdministrativeGender


class PatientBase(FHIRBaseModel):
    """
    Base schema containing common Patient attributes.
    """

    active: Optional[bool] = Field(
        None,
        description="Whether the patient record is active.",
    )

    first_name: Optional[str] = Field(
        None,
        description="Patient's given name.",
        max_length=100,
    )

    middle_name: Optional[str] = Field(
        None,
        description="Patient's middle name.",
        max_length=100,
    )

    last_name: Optional[str] = Field(
        None,
        description="Patient's family name.",
        max_length=100,
    )

    gender: Optional[AdministrativeGender] = Field(
        None,
        description="Administrative gender of the patient.",
        examples=["male", "female", "other", "unknown"],
    )

    birth_date: Optional[date] = Field(
        None,
        description="Date of birth of the patient.",
    )

    deceased_boolean: Optional[bool] = Field(
        None,
        description="Indicates if the patient is deceased.",
    )

    deceased_dateTime: Optional[datetime] = Field(
        None,
        description="Date and time of death if known.",
    )

    marital_status: Optional[str] = Field(
        None,
        description="Marital status of the patient.",
        examples=["single", "married", "divorced", "widowed"],
    )


class PatientCreateSchema(FHIRCreateSchema, PatientBase):
    """
    Schema used for creating a new Patient record.
    """

    resourceType: Literal["Patient"] = Field(
        "Patient",
        description="FHIR resource type. Must always be 'Patient'.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resourceType": "Patient",
                "active": True,
                "first_name": "John",
                "middle_name": "Andrew",
                "last_name": "Doe",
                "gender": "male",
                "birth_date": "1985-04-12",
                "marital_status": "married",
                "deceased_boolean": False,
            }
        }
    )


class PatientResponseSchema(FHIRResponseSchema, PatientBase):
    """
    Schema returned when retrieving a Patient resource.
    """

    resourceType: Literal["Patient"] = Field(
        "Patient",
        description="FHIR resource type.",
    )

    id: int = Field(
        ...,
        description="Internal database identifier for the patient.",
        example=1,
    )

    patient_id: int = Field(
        ...,
        description="Hospital-assigned patient identifier starting from 10000.",
        example=10000,
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "resourceType": "Patient",
                "id": 1,
                "patient_id": 10000,
                "active": True,
                "first_name": "John",
                "middle_name": "Andrew",
                "last_name": "Doe",
                "gender": "male",
                "birth_date": "1985-04-12",
                "marital_status": "married",
                "deceased_boolean": False,
            }
        },
    )
