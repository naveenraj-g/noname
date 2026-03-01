from pydantic import Field
from app.schemas.base import FHIRBaseModel


class FHIRResourceBase(FHIRBaseModel):
    """
    Base class for all FHIR resources.
    """

    resourceType: str = Field(..., description="FHIR resource type name.")


class FHIRCreateSchema(FHIRResourceBase):
    """
    Base schema for resource creation.
    """

    # No id during creation
    pass


class FHIRResponseSchema(FHIRResourceBase):
    """
    Base schema returned by API responses.
    """

    id: str = Field(..., description="FHIR logical identifier assigned by the server.")
