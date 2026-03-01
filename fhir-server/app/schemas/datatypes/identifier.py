from typing import Optional
from pydantic import Field, model_validator
from app.schemas.base import FHIRBaseModel
from app.schemas.datatypes.enums.identifier import IdentifierUse
from app.schemas.datatypes.codable_concept import CodeableConcept
from app.schemas.datatypes.period import Period
from app.schemas.datatypes.reference import Reference


class Identifier(FHIRBaseModel):
    """
    Generic FHIR Identifier datatype.

    An identifier — identifies some entity uniquely and unambiguously.
    Typically used for business identifiers such as medical record numbers,
    national IDs, or license numbers.

    Structure only. Meaning depends on the resource using it.
    """

    use: Optional[IdentifierUse] = Field(
        None,
        description="Purpose of this identifier (usual, official, temp, secondary, old).",
    )

    type: Optional[CodeableConcept] = Field(
        None,
        description="Description of identifier type (e.g., MRN, SSN, Driver's License).",
    )

    system: Optional[str] = Field(
        None,
        description="Namespace URI defining the identifier system.",
        examples=["http://hospital.smarthealth.org/mrn"],
    )

    value: Optional[str] = Field(
        None,
        description="The identifier value within the given system namespace.",
        examples=["12345678"],
    )

    period: Optional[Period] = Field(
        None,
        description="Time period during which the identifier is/was valid.",
    )

    assigner: Optional[Reference] = Field(
        None,
        description="Organization that issued the identifier.",
    )

    @model_validator(mode="after")
    def validate_identifier(self):
        """
        Ensure that an identifier has at least a value or system.
        """
        if not self.value and not self.system:
            raise ValueError("Identifier must have at least 'value' or 'system'.")
        return self
