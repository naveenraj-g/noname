from typing import Optional
from pydantic import Field, model_validator
from app.schemas.base import FHIRBaseModel
from app.schemas.datatypes.identifier import Identifier


class Reference(FHIRBaseModel):
    """
    FHIR Reference datatype.

    A reference from one resource to another.
    """

    reference: Optional[str] = Field(
        None,
        title="Reference",
        description="Literal reference to another resource (e.g., 'Patient/123').",
        example="Patient/123",
    )

    type: Optional[str] = Field(
        None,
        title="Reference Type",
        description="The expected resource type (e.g., 'Patient', 'Practitioner').",
        example="Patient",
    )

    identifier: Optional[Identifier] = Field(
        None,
        title="Logical Reference Identifier",
        description="Logical reference when literal reference is not known.",
    )

    display: Optional[str] = Field(
        None,
        title="Display Text",
        description="Text alternative for the resource.",
        example="John Doe",
    )

    @model_validator(mode="after")
    def validate_reference(self):
        """
        Ensure at least one meaningful reference field exists.
        """
        if not any([self.reference, self.identifier, self.display]):
            raise ValueError(
                "Reference must contain at least one of: reference, identifier, or display."
            )

        return self
