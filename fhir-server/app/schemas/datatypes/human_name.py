from typing import Optional, List
from pydantic import Field, model_validator
from app.schemas.base import FHIRBaseModel
from app.schemas.datatypes.enums.human_name import HumanNameUse
from app.schemas.datatypes.period import Period


class HumanName(FHIRBaseModel):
    """
    FHIR HumanName datatype.

    A structured representation of a person's name.
    Used in resources such as Patient, Practitioner, and RelatedPerson.
    """

    use: Optional[HumanNameUse] = Field(
        None,
        title="Name Use",
        description=(
            "Designates which name to use in a particular context. "
            "'official' is the legal name. 'usual' is the name commonly used. "
            "'nickname' for informal names. 'maiden' for pre-marriage family name."
        ),
        example="official",
    )

    text: Optional[str] = Field(
        None,
        title="Full Name Text",
        description=(
            "The complete human-readable name as a single string, "
            "typically formatted as 'Given Family'."
        ),
        example="John A Doe",
    )

    family: Optional[str] = Field(
        None,
        title="Family Name",
        description="The family name (surname/last name) of the person.",
        example="Doe",
    )

    given: Optional[List[str]] = Field(
        None,
        title="Given Names",
        description=(
            "The given names (first name and middle names) of the person. "
            "The first element is the primary given name."
        ),
        example=["John", "A"],
    )

    prefix: Optional[List[str]] = Field(
        None,
        title="Name Prefix",
        description=("Parts that come before the name, such as titles or honorifics."),
        example=["Dr."],
    )

    suffix: Optional[List[str]] = Field(
        None,
        title="Name Suffix",
        description=(
            "Parts that come after the name, such as qualifications or generational indicators."
        ),
        example=["Jr."],
    )

    period: Optional[Period] = Field(
        None,
        title="Validity Period",
        description=("The time period during which this name was/is in use."),
    )

    @model_validator(mode="after")
    def validate_human_name(self):
        """
        Ensure that at least one meaningful name component is present.
        """

        if not self.text and not self.family and not self.given:
            raise ValueError(
                "HumanName must contain at least one of: text, family, or given."
            )

        # Auto-generate text if missing
        if not self.text:
            parts = []
        if self.given:
            parts.extend(self.given)
        if self.family:
            parts.append(self.family)

        if parts:
            self.text = " ".join(parts)

        return self
