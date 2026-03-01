from enum import Enum


class PatientLinkType(str, Enum):
    """
    FHIR Patient.link.type value set.
    """

    replaced_by = "replaced-by"
    replaces = "replaces"
    refer = "refer"
    seealso = "seealso"
