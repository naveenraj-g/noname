from typing import Optional
from pydantic import Field
from schemas.base import FHIRBaseModel


class Coding(FHIRBaseModel):
    """
    Generic FHIR Coding datatype.

    Represents a single code from a terminology system.

    Contains the system URI, code value, optional version, display text,
    and user selection indicator.
    """

    system: Optional[str] = Field(
        None,
        description="Identity of the terminology system (e.g. SNOMED, LOINC, RxNorm).",
        examples=["http://snomed.info/sct"],
    )

    version: Optional[str] = Field(
        None,
        description="Version of the terminology system.",
    )

    code: Optional[str] = Field(
        None,
        description="Symbol in syntax defined by the system.",
        examples=["44054006"],
    )

    display: Optional[str] = Field(
        None,
        description="Representation defined by the system.",
        examples=["Diabetes mellitus type 2"],
    )

    userSelected: Optional[bool] = Field(
        None,
        description="Indicates whether this coding was chosen directly by the user.",
    )
