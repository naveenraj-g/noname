from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# --- FHIR Data Types (Sub-models) ---

class Identifier(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None
    use: Optional[str] = Field(None, pattern="^(usual|official|temp|secondary|old)$")

class HumanName(BaseModel):
    use: Optional[str] = Field(None, pattern="^(usual|official|temp|nickname|anonymous|old|maiden)$")
    family: Optional[str] = None
    given: Optional[List[str]] = None
    text: Optional[str] = None
    prefix: Optional[List[str]] = None  # Dr., Prof., etc
    suffix: Optional[List[str]] = None  # Jr., Sr., PhD, etc

class Telecom(BaseModel):
    system: Optional[str] = Field(None, pattern="^(phone|fax|email|pager|url|sms|other)$")
    value: Optional[str] = None
    use: Optional[str] = Field(None, pattern="^(home|work|temp|old|mobile)$")
    rank: Optional[int] = None

class Address(BaseModel):
    use: Optional[str] = Field(None, pattern="^(home|work|temp|old|billing)$")
    type: Optional[str] = Field(None, pattern="^(postal|physical|both)$")
    line: Optional[List[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None

class QualificationIdentifier(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None

class QualificationCode(BaseModel):
    text: Optional[str] = None  # e.g., "MD", "Board Certified in Cardiology"

class QualificationIssuer(BaseModel):
    display: Optional[str] = None  # Organization name

class Qualification(BaseModel):
    identifier: Optional[List[QualificationIdentifier]] = None
    code: Optional[QualificationCode] = None
    issuer: Optional[QualificationIssuer] = None

# --- Main Practitioner Model ---

class PractitionerCreateSchema(BaseModel):
    resourceType: str = Field("Practitioner", pattern="^Practitioner$")
    active: Optional[bool] = True
    identifier: Optional[List[Identifier]] = None
    name: Optional[List[HumanName]] = None
    telecom: Optional[List[Telecom]] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other|unknown)$")
    birthDate: Optional[date] = None
    address: Optional[List[Address]] = None
    qualification: Optional[List[Qualification]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "resourceType": "Practitioner",
                "active": True,
                "identifier": [
                    {
                        "system": "http://hospital.goodhealth.com/practitioners",
                        "value": "PRAC-789456",
                        "use": "official"
                    }
                ],
                "name": [
                    {
                        "use": "official",
                        "family": "Smith",
                        "given": ["Jane", "Marie"],
                        "prefix": ["Dr."],
                        "text": "Dr. Jane Marie Smith"
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": "+1-555-987-6543",
                        "use": "work",
                        "rank": 1
                    },
                    {
                        "system": "email",
                        "value": "dr.smith@hospital.com",
                        "use": "work"
                    }
                ],
                "gender": "female",
                "birthDate": "1978-03-15",
                "address": [
                    {
                        "use": "work",
                        "type": "physical",
                        "line": ["456 Hospital Drive", "Suite 200"],
                        "city": "Boston",
                        "state": "MA",
                        "postalCode": "02101",
                        "country": "USA"
                    }
                ],
                "qualification": [
                    {
                        "identifier": [
                            {
                                "system": "http://medical.board.org",
                                "value": "MD-123456"
                            }
                        ],
                        "code": {
                            "text": "MD - Doctor of Medicine"
                        },
                        "issuer": {
                            "display": "American Board of Medical Specialties"
                        }
                    }
                ]
            }
        }
