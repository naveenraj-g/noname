from enum import Enum


class PatientGeneralPractitionerRefType(str, Enum):
    PRACTITIONER = "Practitioner"
    PRACTITIONER_ROLE = "PractitionerRole"
    ORGANIZATION = "Organization"


class PatientLinkOtherRefType(str, Enum):
    PATIENT = "Patient"
    RELATED_PERSON = "RelatedPerson"


class PatientLinkType(str, Enum):
    replaced_by = "replaced-by"
    replaces = "replaces"
    refer = "refer"
    seealso = "seealso"


class PatientTelecomContactPointSystem(str, Enum):
    phone = "phone"
    fax = "fax"
    email = "email"
    pager = "pager"
    url = "url"
    sms = "sms"
    other = "other"


class PatientTelecomContactPointUse(str, Enum):
    home = "home"
    work = "work"
    temp = "temp"
    old = "old"
    mobile = "mobile"


class PatientAddressUse(str, Enum):
    home = "home"
    work = "work"
    temp = "temp"
    old = "old"
    billing = "billing"


class PatientAddressType(str, Enum):
    postal = "postal"
    physical = "physical"
    both = "both"
