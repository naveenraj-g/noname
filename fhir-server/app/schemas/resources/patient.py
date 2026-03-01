from typing import List, Optional, Literal
from datetime import date, datetime, timezone
from pydantic import Field, ConfigDict, model_validator

from app.schemas.base import FHIRBaseModel
from app.schemas.resources.base_resource import (
    FHIRCreateSchema,
    FHIRResponseSchema,
)
from app.schemas.datatypes.identifier import Identifier
from app.schemas.datatypes.human_name import HumanName
from app.schemas.datatypes.contact_point import ContactPoint
from app.schemas.datatypes.address import Address
from app.schemas.datatypes.codable_concept import CodeableConcept
from app.schemas.datatypes.attachment import Attachment
from app.schemas.datatypes.reference import Reference
from app.schemas.datatypes.extension import Extension

from app.schemas.datatypes.enums.adminstrative import AdministrativeGender

from app.schemas.resources.backbones.patient import (
    PatientContact,
    PatientCommunication,
    PatientLink,
)


# ─────────────────────────────────────────────────────────────
# Shared Patient Fields
# ─────────────────────────────────────────────────────────────


class PatientBase(FHIRBaseModel):
    """
    Core FHIR Patient resource fields.

    Represents demographic, administrative, and contact information
    for an individual receiving healthcare services.
    """

    identifier: Optional[List[Identifier]] = Field(
        None,
        description=(
            "Business identifiers assigned to this patient. "
            "Examples include Medical Record Number (MRN), "
            "national ID, or insurance policy number."
        ),
    )

    active: Optional[bool] = Field(
        True,
        description="Whether this patient record is currently active.",
        example=True,
    )

    name: Optional[List[HumanName]] = Field(
        None,
        description="Names associated with the patient (legal, maiden, nickname, etc.).",
    )

    telecom: Optional[List[ContactPoint]] = Field(
        None,
        description="Contact details such as phone numbers or email addresses.",
    )

    gender: Optional[AdministrativeGender] = Field(
        None,
        description="Administrative gender for record-keeping purposes.",
        example="male",
    )

    birthDate: Optional[date] = Field(
        None,
        description="Date of birth in ISO 8601 format (YYYY-MM-DD).",
        example="1985-04-12",
    )

    deceasedBoolean: Optional[bool] = Field(
        None,
        description="Indicates whether the patient is deceased.",
        example=False,
    )

    deceasedDateTime: Optional[datetime] = Field(
        None,
        description="Exact date and time of death if known.",
        examples=["2024-01-10T18:00:00Z"],
    )

    address: Optional[List[Address]] = Field(
        None,
        description="Addresses associated with the patient (home, work, billing).",
    )

    maritalStatus: Optional[CodeableConcept] = Field(
        None,
        description="Marital or civil status of the patient.",
    )

    multipleBirthBoolean: Optional[bool] = Field(
        None,
        description="Indicates if the patient was part of a multiple birth.",
        example=True,
    )

    multipleBirthInteger: Optional[int] = Field(
        None,
        description="Birth order in a multiple birth (1 = first born).",
        example=2,
        ge=1,
    )

    photo: Optional[List[Attachment]] = Field(
        None,
        description="Photographic image of the patient.",
    )

    contact: Optional[List[PatientContact]] = Field(
        None,
        description="A contact party (guardian, partner, emergency contact).",
    )

    communication: Optional[List[PatientCommunication]] = Field(
        None,
        description="Languages the patient is able to communicate in.",
    )

    generalPractitioner: Optional[List[Reference]] = Field(
        None,
        description=(
            "Patient's nominated primary care provider. "
            "May reference Practitioner, PractitionerRole, or Organization."
        ),
    )

    managingOrganization: Optional[Reference] = Field(
        None,
        description="Organization that is responsible for maintaining this patient record.",
    )

    link: Optional[List[PatientLink]] = Field(
        None,
        description="Links to other Patient or RelatedPerson resources concerning the same individual.",
    )

    extension: Optional[List[Extension]] = Field(
        None,
        title="Extension",
        description=(
            "Additional information not part of the basic FHIR definition. "
            "Used to represent extended elements such as birth time."
        ),
    )

    # ─────────────────────────────────────────
    # Validation Rules
    # ─────────────────────────────────────────

    @model_validator(mode="after")
    def validate_patient_rules(self):
        # Rule 1: deceasedBoolean XOR deceasedDateTime
        if self.deceasedBoolean is not None and self.deceasedDateTime is not None:
            raise ValueError(
                "Only one of deceasedBoolean or deceasedDateTime may be provided."
            )

        # Rule 2: multipleBirthBoolean XOR multipleBirthInteger
        if (
            self.multipleBirthBoolean is not None
            and self.multipleBirthInteger is not None
        ):
            raise ValueError(
                "Only one of multipleBirthBoolean or multipleBirthInteger may be provided."
            )

        # Rule 3: birthDate cannot be in future
        if self.birthDate and self.birthDate > date.today():
            raise ValueError("birthDate cannot be in the future.")

        # Rule 4: deceasedDateTime cannot be in future
        if self.deceasedDateTime and self.deceasedDateTime > datetime.now(timezone.utc):
            raise ValueError("deceasedDateTime cannot be in the future.")

        return self


# ─────────────────────────────────────────────────────────────
# Create Schema
# ─────────────────────────────────────────────────────────────


class PatientCreateSchema(FHIRCreateSchema, PatientBase):
    """
    Schema used for creating a new Patient resource.
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
                "identifier": [
                    {
                        "system": "http://hospital.goodhealth.com/mrn",
                        "value": "MRN-123456",
                        "use": "official",
                    }
                ],
                "name": [
                    {
                        "use": "official",
                        "family": "Doe",
                        "given": ["John", "A"],
                        "text": "John A Doe",
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": "+1-555-123-4567",
                        "use": "mobile",
                        "rank": 1,
                    }
                ],
                "gender": "male",
                "birthDate": "1985-04-12",
                "address": [
                    {
                        "use": "home",
                        "line": ["123 Main Street"],
                        "city": "New York",
                        "state": "NY",
                        "postalCode": "10001",
                        "country": "USA",
                    }
                ],
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/patient-birthTime",
                        "valueDateTime": "1985-04-12T08:30:00Z",
                    }
                ],
            }
        }
    )


# ─────────────────────────────────────────────────────────────
# Response Schema
# ─────────────────────────────────────────────────────────────


class PatientResponseSchema(FHIRResponseSchema, PatientBase):
    """
    Schema returned when retrieving a Patient resource.
    """

    resourceType: Literal["Patient"] = Field(
        "Patient",
        description="FHIR resource type.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123",
                "resourceType": "Patient",
                "meta": {"versionId": "2", "lastUpdated": "2026-02-28T12:30:00Z"},
                "active": True,
                "name": [{"family": "Doe", "given": ["John"]}],
                "gender": "male",
                "birthDate": "1985-04-12",
            }
        }
    )
