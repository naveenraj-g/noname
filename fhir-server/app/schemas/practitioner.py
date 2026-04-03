from datetime import date
from typing import List, Optional
from typing_extensions import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import (
    AdministrativeGender,
    ContactPointSystem,
    ContactPointUse,
    AddressUse,
    AddressType,
    IdentifierUse,
    HumanNameUse,
)


# ── FHIR datatype fragments (response-only) ────────────────────────────────


class FHIRPractitionerIdentifier(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    system: Optional[str] = None
    value: Optional[str] = None
    use: Optional[str] = None


class FHIRHumanName(BaseModel):
    use: Optional[str] = None
    family: Optional[str] = None
    given: List[str] = []
    text: Optional[str] = None
    prefix: List[str] = []
    suffix: List[str] = []


class FHIRPractitionerTelecom(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None
    use: Optional[str] = None
    rank: Optional[int] = None


class FHIRPractitionerAddress(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    use: Optional[str] = None
    type: Optional[str] = None
    text: Optional[str] = None
    line: List[str] = []
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None


class FHIRQualificationIdentifier(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None


class FHIRQualificationCode(BaseModel):
    text: Optional[str] = None


class FHIRQualificationIssuer(BaseModel):
    display: Optional[str] = None


class FHIRQualification(BaseModel):
    identifier: Optional[List[FHIRQualificationIdentifier]] = None
    code: Optional[FHIRQualificationCode] = None
    issuer: Optional[FHIRQualificationIssuer] = None


# ── Sub-resource create schemas ────────────────────────────────────────────


class PractitionerIdentifierCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: Optional[str] = Field(None, description="URI of the identifier namespace (e.g. NPI system).")
    value: str = Field(..., description="Identifier value (e.g. NPI number, license number).")
    use: Optional[IdentifierUse] = Field(None, description="Purpose of this identifier.")


class PractitionerNameCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    use: Optional[HumanNameUse] = Field(None, description="Purpose of this name.")
    family: Optional[str] = Field(None, max_length=100, description="Family name (surname).")
    given: Optional[List[str]] = Field(None, description="Given names — first name, then middle names.")
    text: Optional[str] = Field(None, description="Full name as a single string, e.g. 'Dr. Jane M. Smith MD'.")
    prefix: Optional[List[str]] = Field(None, description="Honorific prefixes, e.g. ['Dr.', 'Prof.'].")
    suffix: Optional[List[str]] = Field(None, description="Professional suffixes, e.g. ['MD', 'PhD'].")


class PractitionerTelecomCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: ContactPointSystem = Field(..., description="Type of contact point.")
    value: str = Field(..., description="Contact value (phone number, email address, etc.).")
    use: Optional[ContactPointUse] = Field(None, description="Purpose of this contact point.")
    rank: Optional[int] = Field(None, ge=1, description="Preferred contact order (1 = most preferred).")


class PractitionerAddressCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    use: Optional[AddressUse] = Field(None, description="Purpose of this address.")
    type: Optional[AddressType] = Field(None, description="postal | physical | both.")
    text: Optional[str] = Field(None, description="Full address as plain text.")
    line: Optional[str] = Field(None, description="Street address line(s), comma-separated for multiple.")
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class PractitionerQualificationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identifier_system: Optional[str] = Field(None, description="Namespace URI for the qualification identifier.")
    identifier_value: Optional[str] = Field(None, description="Qualification or license number.")
    code_text: Optional[str] = Field(None, description="Human-readable qualification type, e.g. 'MD - Doctor of Medicine'.")
    issuer: Optional[str] = Field(None, description="Display name of the issuing organization.")


# ── Practitioner create / patch ────────────────────────────────────────────


class PractitionerCreateSchema(BaseModel):
    """
    Payload accepted when creating a new Practitioner (core demographics only).
    Sub-resources (names, identifiers, telecom, addresses, qualifications) are
    added via their respective POST sub-resource endpoints.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "active": True,
                "gender": "female",
                "birth_date": "1978-03-15",
            }
        },
    )

    active: Optional[bool] = True
    gender: Optional[AdministrativeGender] = None
    birth_date: Optional[date] = None


class PractitionerPatchSchema(BaseModel):
    """Partial-update payload — only supplied fields are written."""

    model_config = ConfigDict(extra="forbid")

    active: Optional[bool] = None
    gender: Optional[AdministrativeGender] = None
    birth_date: Optional[date] = None


# ── Practitioner response ──────────────────────────────────────────────────


class PractitionerResponseSchema(BaseModel):
    """
    FHIR R4 Practitioner resource returned by all read/write endpoints.

    - `id` is the PUBLIC practitioner_id (e.g. 30001) — the internal DB pk is never included.
    - Sub-resources are omitted when empty.
    """

    model_config = ConfigDict(populate_by_name=True)

    resourceType: Literal["Practitioner"] = "Practitioner"
    id: str = Field(..., description="Public practitioner identifier (e.g. '30001').")
    active: Optional[bool] = None
    gender: Optional[str] = None
    birthDate: Optional[date] = None
    identifier: Optional[List[FHIRPractitionerIdentifier]] = None
    name: Optional[List[FHIRHumanName]] = None
    telecom: Optional[List[FHIRPractitionerTelecom]] = None
    address: Optional[List[FHIRPractitionerAddress]] = None
    qualification: Optional[List[FHIRQualification]] = None
