from enum import Enum


class AdministrativeGender(str, Enum):
    """
    FHIR AdministrativeGender value set.

    The gender of a person for administrative purposes.
    """

    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"
