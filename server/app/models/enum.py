import enum


class ParticipantReferenceType(str, enum.Enum):
    PATIENT = "PATIENT"
    PRACTITIONER = "PRACTITIONER"
