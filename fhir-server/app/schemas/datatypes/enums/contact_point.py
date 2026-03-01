from enum import Enum


class ContactPointSystem(str, Enum):
    """
    FHIR ContactPointSystem value set.

    Telecommunications form for contact point.
    """

    phone = "phone"
    fax = "fax"
    email = "email"
    pager = "pager"
    url = "url"
    sms = "sms"
    other = "other"


class ContactPointUse(str, Enum):
    """
    FHIR ContactPointUse value set.

    Purpose of the contact point.
    """

    home = "home"
    work = "work"
    temp = "temp"
    old = "old"
    mobile = "mobile"
