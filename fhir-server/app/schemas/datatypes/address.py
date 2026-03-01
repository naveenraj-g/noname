from typing import Optional, List
from pydantic import Field, model_validator
from app.schemas.base import FHIRBaseModel
from app.schemas.datatypes.enums.address import AddressUse, AddressType
from app.schemas.datatypes.period import Period


class Address(FHIRBaseModel):
    """
    FHIR Address datatype.

    An address expressed using postal conventions (as opposed to GPS or other location definition formats).
    """

    use: Optional[AddressUse] = Field(
        None,
        title="Address Use",
        description="The purpose of this address.",
        example="home",
    )

    type: Optional[AddressType] = Field(
        None,
        title="Address Type",
        description="Distinguishes between physical and postal address.",
        example="both",
    )

    text: Optional[str] = Field(
        None,
        title="Full Address Text",
        description="The full address as a single text string.",
        example="221B Baker Street, London NW1 6XE, UK",
    )

    line: Optional[List[str]] = Field(
        None,
        title="Street Address Lines",
        description="Street name, number, direction, and other components.",
        example=["221B Baker Street"],
    )

    city: Optional[str] = Field(
        None,
        title="City",
        description="The name of the city, town, or municipality.",
        example="London",
    )

    district: Optional[str] = Field(
        None,
        title="District",
        description="District or county within a state.",
        example="Greater London",
    )

    state: Optional[str] = Field(
        None,
        title="State or Province",
        description="Sub-unit of a country (e.g., state or province).",
        example="England",
    )

    postalCode: Optional[str] = Field(
        None,
        title="Postal Code",
        description="Postal code for the area.",
        example="NW1 6XE",
    )

    country: Optional[str] = Field(
        None,
        title="Country",
        description="Country (can be ISO 3166 2 or 3 letter code).",
        example="GB",
    )

    period: Optional[Period] = Field(
        None,
        title="Validity Period",
        description="Time period when the address was/is in use.",
    )

    @model_validator(mode="after")
    def validate_address(self):
        """
        Ensure at least some address information is present.
        """

        if not any(
            [
                self.text,
                self.line,
                self.city,
                self.state,
                self.postalCode,
                self.country,
            ]
        ):
            raise ValueError(
                "Address must contain at least one meaningful address component."
            )

        return self
