from typing import List, Optional
from pydantic import Field, model_validator
from schemas.base import FHIRBaseModel
from schemas.datatypes.coding import Coding


class CodeableConcept(FHIRBaseModel):
    """
    Generic FHIR CodeableConcept datatype.

    Represents a coded concept with optional terminology system reference
    and/or free-text description.

    Structure only. Meaning depends on the resource using it.
    """

    coding: Optional[List[Coding]] = Field(
        None,
        description="Code defined by a terminology system.",
    )

    text: Optional[str] = Field(
        None,
        description="Plain text representation of the concept.",
    )

    @model_validator(mode="after")
    def validate_presence(self):
        """
        Ensure at least one of coding or text is present.
        FHIR allows either, but not both empty.
        """
        if not self.coding and not self.text:
            raise ValueError("CodeableConcept must have at least 'coding' or 'text'")
        return self
