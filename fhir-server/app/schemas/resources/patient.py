from datetime import date
from typing import List, Optional
from typing_extensions import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import AdministrativeGender, ContactPointSystem, ContactPointUse


# ── FHIR datatype fragments (response-only) ────────────────────────────────


class FHIRIdentifier(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    system: Optional[str] = None
    value: Optional[str] = None


class FHIRHumanName(BaseModel):
    use: Optional[str] = None
    family: Optional[str] = None
    given: List[str] = []


class FHIRTelecom(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None
    use: Optional[str] = None


class FHIRAddress(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    line: List[str] = []
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None


# ── Sub-resource create schemas ────────────────────────────────────────────


class IdentifierCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: Optional[str] = Field(None, description="URI of the identifier namespace.")
    value: str = Field(..., description="Identifier value within the given system.")


class TelecomCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: ContactPointSystem = Field(..., description="Type of contact point.")
    value: str = Field(..., description="Contact point value (phone number, email, etc.).")
    use: Optional[ContactPointUse] = Field(None, description="Purpose of this contact point.")


class AddressCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line: Optional[str] = Field(None, description="Street address line (e.g. '123 Main St').")
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


# ── Patient create / patch ─────────────────────────────────────────────────


class PatientCreateSchema(BaseModel):
    """Payload accepted when creating a new Patient (basic demographics only)."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "given_name": "John",
                "family_name": "Doe",
                "gender": "male",
                "birth_date": "1985-04-12",
                "active": True,
            }
        },
    )

    given_name: Optional[str] = Field(None, max_length=100)
    family_name: Optional[str] = Field(None, max_length=100)
    gender: Optional[AdministrativeGender] = None
    birth_date: Optional[date] = None
    active: Optional[bool] = True


class PatientPatchSchema(BaseModel):
    """Partial-update payload — only supplied fields are written."""

    model_config = ConfigDict(extra="forbid")

    given_name: Optional[str] = Field(None, max_length=100)
    family_name: Optional[str] = Field(None, max_length=100)
    gender: Optional[AdministrativeGender] = None
    birth_date: Optional[date] = None
    active: Optional[bool] = None


# ── Patient response ───────────────────────────────────────────────────────


class PatientResponseSchema(BaseModel):
    """
    FHIR R4 Patient resource returned by all read/write endpoints.

    - `id` is the PUBLIC patient_id (e.g. 10001) — the internal DB pk is
      never included.
    - Sub-resources (identifier, telecom, address) are omitted when empty.
    """

    model_config = ConfigDict(populate_by_name=True)

    resourceType: Literal["Patient"] = "Patient"
    id: str = Field(..., description="Public patient identifier (e.g. '10001').")
    active: Optional[bool] = None
    name: Optional[List[FHIRHumanName]] = None
    gender: Optional[str] = None
    birthDate: Optional[date] = None
    identifier: Optional[List[FHIRIdentifier]] = None
    telecom: Optional[List[FHIRTelecom]] = None
    address: Optional[List[FHIRAddress]] = None
