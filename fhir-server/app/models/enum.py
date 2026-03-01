from enum import Enum


class SubjectReferenceType(str, Enum):
    """FHIR subject reference types for Encounter.subject."""

    PATIENT = "Patient"
    GROUP = "Group"


class ParticipantReferenceType(str, Enum):
    """FHIR individual reference types for Encounter.participant.individual."""

    PATIENT = "Patient"
    PRACTITIONER = "Practitioner"
    PRACTITIONER_ROLE = "PractitionerRole"
    RELATED_PERSON = "RelatedPerson"


class GenderType(str, Enum):
    """
    FHIR AdministrativeGender value set.

    The gender of a person for administrative purposes.
    """

    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"
