from typing import Optional, List
from pydantic import Field, model_validator
from app.schemas.base import FHIRBaseModel
from app.schemas.datatypes import HumanName
from app.schemas.datatypes import ContactPoint
from app.schemas.datatypes import Address
from app.schemas.datatypes import Period
from app.schemas.datatypes import Reference
from app.schemas.datatypes import CodeableConcept
from app.schemas.enums import AdministrativeGender
from app.schemas.enums import PatientLinkType


class PatientContact(FHIRBaseModel):
    """
    Patient.contact backbone element.

    A contact party (e.g., guardian, partner, friend) for the patient.
    """

    relationship: Optional[List[CodeableConcept]] = Field(
        None,
        description="The kind of relationship (e.g., parent, guardian, emergency contact).",
    )

    name: Optional[HumanName] = Field(
        None,
        description="Name of the contact person.",
    )

    telecom: Optional[List[ContactPoint]] = Field(
        None,
        description="Contact details (phone, email, etc.) for the contact person.",
    )

    address: Optional[Address] = Field(
        None,
        description="Address of the contact person.",
    )

    gender: Optional[AdministrativeGender] = Field(
        None,
        description="Administrative gender of the contact person.",
    )

    organization: Optional[Reference] = Field(
        None,
        description="Organization associated with the contact.",
    )

    period: Optional[Period] = Field(
        None,
        description="The period during which this contact is valid.",
    )

    @model_validator(mode="after")
    def validate_contact(self):
        """
        Ensure that the contact contains at least one meaningful detail.
        """
        if not any(
            [
                self.relationship,
                self.name,
                self.telecom,
                self.address,
                self.organization,
            ]
        ):
            raise ValueError(
                "Patient.contact must contain at least one meaningful field."
            )

        return self


class PatientCommunication(FHIRBaseModel):
    """
    Patient.communication backbone element.

    A language which may be used to communicate with the patient.
    """

    language: CodeableConcept = Field(
        ...,
        description="The language which can be used to communicate with the patient.",
    )

    preferred: Optional[bool] = Field(
        None,
        description="Indicates whether this language is preferred.",
        example=True,
    )


class PatientLink(FHIRBaseModel):
    """
    Patient.link backbone element.

    Link to another patient or related person resource.
    """

    other: Reference = Field(
        ...,
        description="The other patient or related person resource.",
    )

    type: PatientLinkType = Field(
        ...,
        description="The type of link between this patient and the other resource.",
    )
