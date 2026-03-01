from typing import Optional
from pydantic import Field, model_validator
from app.schemas.base import FHIRBaseModel
from app.schemas.datatypes.enums.contact_point import (
    ContactPointSystem,
    ContactPointUse,
)
from app.schemas.datatypes.period import Period
import re


class ContactPoint(FHIRBaseModel):
    """
    FHIR ContactPoint datatype.

    Details for all kinds of technology-mediated contact points
    for a person or organization.
    """

    system: Optional[ContactPointSystem] = Field(
        None,
        title="Contact System",
        description="Telecommunications form for contact point.",
        example="phone",
    )

    value: Optional[str] = Field(
        None,
        title="Contact Value",
        description="The actual contact point details (e.g., phone number or email address).",
        example="+91-9876543210",
    )

    use: Optional[ContactPointUse] = Field(
        None,
        title="Contact Use",
        description="Identifies the purpose for the contact point.",
        example="mobile",
    )

    rank: Optional[int] = Field(
        None,
        title="Preference Rank",
        description="Specifies a preferred order in which to use a set of contacts (1 = highest priority).",
        example=1,
        ge=1,
    )

    period: Optional[Period] = Field(
        None,
        title="Validity Period",
        description="Time period when the contact point was/is in use.",
    )

    @model_validator(mode="after")
    def validate_contact_point(self):
        """
        Ensure meaningful ContactPoint data exists.
        """

        if not self.value:
            raise ValueError("ContactPoint must include a value.")

        if self.system == ContactPointSystem.email:
            email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
            if not re.match(email_pattern, self.value):
                raise ValueError("Invalid email format.")

        return self
