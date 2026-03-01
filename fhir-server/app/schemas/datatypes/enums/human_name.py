from enum import Enum


class HumanNameUse(str, Enum):
    """
    FHIR HumanNameUse value set.

    Indicates the purpose of this name.
    """

    usual = "usual"  # The name normally used
    official = "official"  # Official/legal name
    temp = "temp"  # Temporary name
    nickname = "nickname"  # Nickname
    anonymous = "anonymous"  # Anonymous/pseudonym
    old = "old"  # Old/previous name
    maiden = "maiden"  # Maiden name
