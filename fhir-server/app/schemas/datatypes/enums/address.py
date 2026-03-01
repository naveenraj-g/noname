from enum import Enum


class AddressUse(str, Enum):
    """
    FHIR AddressUse value set.

    The purpose of this address.
    """

    home = "home"
    work = "work"
    temp = "temp"
    old = "old"
    billing = "billing"


class AddressType(str, Enum):
    """
    FHIR AddressType value set.

    The type of address.
    """

    postal = "postal"
    physical = "physical"
    both = "both"
