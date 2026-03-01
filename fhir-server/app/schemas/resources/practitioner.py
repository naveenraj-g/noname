from typing import List, Optional, Literal
from pydantic import Field
from app.schemas.base import FHIRBaseModel
from app.schemas.datatypes.identifier import Identifier


class PractitionerBase(FHIRBaseModel):
    identifier: Optional[List[Identifier]] = Field(
        None,
        description="Practitioner identifiers such as medical license number or NPI.",
        examples=[
            [
                {
                    "system": "http://hl7.org/fhir/sid/us-npi",
                    "value": "1234567890",
                    "use": "official",
                }
            ]
        ],
    )
