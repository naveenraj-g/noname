from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date


# ── FHIR Data Types (Sub-models) ──────────────────────────────────────


class Identifier(BaseModel):
    """A unique identifier assigned to a practitioner, such as a medical license number or NPI."""

    system: Optional[str] = Field(
        None,
        title="Identifier System",
        description="The namespace URI for the identifier value. Typically a URL identifying the assigning authority, e.g. 'http://hospital.goodhealth.com/practitioners'.",
        example="http://hospital.goodhealth.com/practitioners",
    )
    value: Optional[str] = Field(
        None,
        title="Identifier Value",
        description="The actual identifier that uniquely identifies this practitioner within the namespace — e.g., a medical license number or employee ID.",
        example="PRAC-789456",
    )
    use: Optional[Literal["usual", "official", "temp", "secondary", "old"]] = Field(
        None,
        title="Identifier Use",
        description="The purpose of this identifier. 'official' for the primary organizational identifier, 'usual' for commonly used identifiers.",
        example="official",
    )


class HumanName(BaseModel):
    """A practitioner's name including professional prefixes and suffixes."""

    use: Optional[Literal["usual", "official", "temp", "nickname", "anonymous", "old", "maiden"]] = Field(
        None,
        title="Name Use",
        description="Designates which name to use in a particular context. 'official' is the legal name, 'usual' is the commonly used professional name.",
        example="official",
    )
    family: Optional[str] = Field(
        None,
        title="Family Name",
        description="The family name (surname/last name) of the practitioner.",
        example="Smith",
    )
    given: Optional[List[str]] = Field(
        None,
        title="Given Names",
        description="The given names (first name and middle names) of the practitioner.",
        example=["Jane", "Marie"],
    )
    text: Optional[str] = Field(
        None,
        title="Full Name Text",
        description="The complete human-readable name as a single string, including any professional titles.",
        example="Dr. Jane Marie Smith",
    )
    prefix: Optional[List[str]] = Field(
        None,
        title="Name Prefixes",
        description="Professional or honorific prefixes such as 'Dr.', 'Prof.', 'Mr.', 'Mrs.'.",
        example=["Dr."],
    )
    suffix: Optional[List[str]] = Field(
        None,
        title="Name Suffixes",
        description="Professional or generational suffixes such as 'Jr.', 'Sr.', 'PhD', 'MD'.",
        example=["MD"],
    )


class Telecom(BaseModel):
    """A contact point for the practitioner — phone, email, or other communication channel."""

    system: Optional[Literal["phone", "fax", "email", "pager", "url", "sms", "other"]] = Field(
        None,
        title="Contact System",
        description="The type of communication system. Use 'phone' for phone numbers, 'email' for email addresses, 'pager' for hospital paging systems.",
        example="phone",
    )
    value: Optional[str] = Field(
        None,
        title="Contact Value",
        description="The actual contact point value — a phone number, email address, or URL.",
        example="+1-555-987-6543",
    )
    use: Optional[Literal["home", "work", "temp", "old", "mobile"]] = Field(
        None,
        title="Contact Use",
        description="The purpose of this contact point. Most practitioner contacts are 'work'. Use 'mobile' for personal mobile numbers.",
        example="work",
    )
    rank: Optional[int] = Field(
        None,
        title="Preference Rank",
        description="Preferred order for using this contact. Lower numbers = higher preference (1 = most preferred).",
        ge=1,
        example=1,
    )


class Address(BaseModel):
    """A physical or mailing address for the practitioner, typically their practice location."""

    use: Optional[Literal["home", "work", "temp", "old", "billing"]] = Field(
        None,
        title="Address Use",
        description="The purpose of this address. 'work' for the practitioner's practice or hospital address.",
        example="work",
    )
    type: Optional[Literal["postal", "physical", "both"]] = Field(
        None,
        title="Address Type",
        description="Distinguishes between a physical location and a mailing address.",
        example="physical",
    )
    line: Optional[List[str]] = Field(
        None,
        title="Street Address Lines",
        description="Street name, number, suite, building, etc.",
        example=["456 Hospital Drive", "Suite 200"],
    )
    city: Optional[str] = Field(
        None,
        title="City",
        description="The name of the city, town, or municipality.",
        example="Boston",
    )
    state: Optional[str] = Field(
        None,
        title="State/Province",
        description="The state, province, or region.",
        example="MA",
    )
    postalCode: Optional[str] = Field(
        None,
        title="Postal Code",
        description="The postal or ZIP code.",
        example="02101",
    )
    country: Optional[str] = Field(
        None,
        title="Country",
        description="The country name or ISO 3166 country code.",
        example="USA",
    )


class QualificationIdentifier(BaseModel):
    """An identifier for a professional qualification or certification."""

    system: Optional[str] = Field(
        None,
        title="Qualification System",
        description="The namespace URI for the qualification identifier, e.g. the medical board's system URL.",
        example="http://medical.board.org",
    )
    value: Optional[str] = Field(
        None,
        title="Qualification Number",
        description="The actual qualification or license number.",
        example="MD-123456",
    )


class QualificationCode(BaseModel):
    """A coded representation of the type of qualification."""

    text: Optional[str] = Field(
        None,
        title="Qualification Description",
        description="A human-readable description of the qualification, e.g. 'MD - Doctor of Medicine', 'Board Certified in Cardiology'.",
        example="MD - Doctor of Medicine",
    )


class QualificationIssuer(BaseModel):
    """The organization that issued or certifies the qualification."""

    display: Optional[str] = Field(
        None,
        title="Issuer Name",
        description="The display name of the organization that issued the qualification, e.g. 'American Board of Medical Specialties'.",
        example="American Board of Medical Specialties",
    )


class Qualification(BaseModel):
    """A professional qualification, certification, or accreditation held by the practitioner."""

    identifier: Optional[List[QualificationIdentifier]] = Field(
        None,
        title="Qualification Identifiers",
        description="Official identifiers for this qualification — license numbers, certification IDs, etc.",
    )
    code: Optional[QualificationCode] = Field(
        None,
        title="Qualification Code",
        description="The type of qualification — what degree, certification, or license this represents.",
    )
    issuer: Optional[QualificationIssuer] = Field(
        None,
        title="Issuing Organization",
        description="The organization that issued or certified the qualification.",
    )


# ── Main Practitioner Model ───────────────────────────────────────────


class PractitionerCreateSchema(BaseModel):
    """
    Schema for creating a FHIR Practitioner resource.

    A Practitioner is a person who is directly or indirectly involved in the provisioning
    of healthcare. This includes physicians, nurses, pharmacists, therapists, and other
    clinical or administrative staff. All fields follow the HL7 FHIR R4 Practitioner specification.
    """

    resourceType: str = Field(
        "Practitioner",
        title="Resource Type",
        description="The FHIR resource type. Must always be 'Practitioner' for this schema.",
        pattern="^Practitioner$",
        example="Practitioner",
    )
    active: Optional[bool] = Field(
        True,
        title="Active Status",
        description="Whether this practitioner record is currently active. Set to false if the practitioner is no longer practicing or has left the organization.",
        example=True,
    )
    identifier: Optional[List[Identifier]] = Field(
        None,
        title="Practitioner Identifiers",
        description="Business identifiers for the practitioner — NPI numbers, medical license numbers, employee IDs, etc.",
    )
    name: Optional[List[HumanName]] = Field(
        None,
        title="Practitioner Names",
        description="The names associated with the practitioner. Include professional prefixes like 'Dr.' and suffixes like 'MD'.",
    )
    telecom: Optional[List[Telecom]] = Field(
        None,
        title="Contact Points",
        description="Contact details for the practitioner — primarily work phone, email, and pager numbers.",
    )
    gender: Optional[Literal["male", "female", "other", "unknown"]] = Field(
        None,
        title="Administrative Gender",
        description="The administrative gender of the practitioner for record-keeping purposes.",
        example="female",
    )
    birthDate: Optional[date] = Field(
        None,
        title="Date of Birth",
        description="The practitioner's date of birth in ISO 8601 format (YYYY-MM-DD).",
        example="1978-03-15",
    )
    address: Optional[List[Address]] = Field(
        None,
        title="Practitioner Addresses",
        description="Addresses associated with the practitioner, typically their practice or hospital location.",
    )
    qualification: Optional[List[Qualification]] = Field(
        None,
        title="Professional Qualifications",
        description="Professional qualifications, certifications, accreditations, and licenses held by the practitioner.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "resourceType": "Practitioner",
                "active": True,
                "identifier": [
                    {
                        "system": "http://hospital.goodhealth.com/practitioners",
                        "value": "PRAC-789456",
                        "use": "official",
                    }
                ],
                "name": [
                    {
                        "use": "official",
                        "family": "Smith",
                        "given": ["Jane", "Marie"],
                        "prefix": ["Dr."],
                        "text": "Dr. Jane Marie Smith",
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": "+1-555-987-6543",
                        "use": "work",
                        "rank": 1,
                    },
                    {
                        "system": "email",
                        "value": "dr.smith@hospital.com",
                        "use": "work",
                    },
                ],
                "gender": "female",
                "birthDate": "1978-03-15",
                "address": [
                    {
                        "use": "work",
                        "type": "physical",
                        "line": ["456 Hospital Drive", "Suite 200"],
                        "city": "Boston",
                        "state": "MA",
                        "postalCode": "02101",
                        "country": "USA",
                    }
                ],
                "qualification": [
                    {
                        "identifier": [
                            {
                                "system": "http://medical.board.org",
                                "value": "MD-123456",
                            }
                        ],
                        "code": {"text": "MD - Doctor of Medicine"},
                        "issuer": {
                            "display": "American Board of Medical Specialties"
                        },
                    }
                ],
            }
        }
